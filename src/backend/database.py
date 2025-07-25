import sqlite3
import json
import os
import shutil
import zipfile
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
import logging
from typing import Optional

class DatabaseManager:
    def __init__(self, db_path="data/freight_loader.db"):
        self.db_path = db_path
        self.backup_dir = "data/backups"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database with enhanced brokerage-centric schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced brokerage configurations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brokerage_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brokerage_name TEXT NOT NULL,
                configuration_name TEXT NOT NULL,
                field_mappings TEXT NOT NULL,
                api_credentials TEXT NOT NULL,
                file_headers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                version INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                description TEXT,
                UNIQUE(brokerage_name, configuration_name)
            )
        ''')
        
        # Enhanced upload history table with better error tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS upload_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brokerage_name TEXT NOT NULL,
                configuration_name TEXT,
                filename TEXT NOT NULL,
                total_records INTEGER,
                successful_records INTEGER,
                failed_records INTEGER,
                error_log TEXT,
                processing_time_seconds REAL,
                file_headers TEXT,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            )
        ''')
        
        # Processing errors table for detailed troubleshooting
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_history_id INTEGER,
                row_number INTEGER,
                field_name TEXT,
                error_type TEXT,
                error_message TEXT,
                suggested_fix TEXT,
                original_value TEXT,
                expected_format TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (upload_history_id) REFERENCES upload_history (id)
            )
        ''')
        
        # Configuration change log for versioning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuration_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                configuration_id INTEGER,
                change_type TEXT NOT NULL, -- 'created', 'updated', 'field_added', 'field_removed', 'field_modified'
                change_description TEXT,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (configuration_id) REFERENCES brokerage_configurations (id)
            )
        ''')
        
        # Legacy table migration - keep old table for backward compatibility
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT UNIQUE NOT NULL,
                field_mappings TEXT NOT NULL,
                api_credentials TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Backup history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                backup_size INTEGER,
                backup_type TEXT NOT NULL,
                checksum TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        ''')
        
        # Learning system tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mapping_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                brokerage_name TEXT NOT NULL,
                configuration_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_headers TEXT,
                suggested_mappings TEXT,
                final_mappings TEXT,
                suggestions_accepted INTEGER DEFAULT 0,
                manual_corrections INTEGER DEFAULT 0,
                processing_success_rate REAL,
                total_fields INTEGER DEFAULT 0,
                user_satisfaction TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mapping_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER,
                column_name TEXT NOT NULL,
                column_sample_data TEXT,
                column_data_type TEXT,
                suggested_field TEXT,
                suggested_confidence REAL,
                actual_field TEXT,
                decision_type TEXT,
                decision_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (interaction_id) REFERENCES mapping_interactions (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brokerage_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brokerage_name TEXT NOT NULL,
                column_pattern TEXT NOT NULL,
                api_field TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                average_confidence REAL DEFAULT 0.0,
                data_type_pattern TEXT,
                sample_values TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(brokerage_name, column_pattern, api_field)
            )
        ''')
        
        # External integrations tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT UNIQUE NOT NULL,
                type_display_name TEXT NOT NULL,
                description TEXT,
                default_config TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS external_integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brokerage_name TEXT NOT NULL,
                integration_name TEXT NOT NULL,
                integration_type_id INTEGER NOT NULL,
                description TEXT,
                config_data TEXT NOT NULL,
                auth_credentials TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                created_by TEXT,
                UNIQUE(brokerage_name, integration_name),
                FOREIGN KEY (integration_type_id) REFERENCES integration_types (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_data_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_id INTEGER NOT NULL,
                source_field TEXT NOT NULL,
                target_field TEXT NOT NULL,
                transformation_rule TEXT,
                is_required BOOLEAN DEFAULT 0,
                default_value TEXT,
                validation_rule TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (integration_id) REFERENCES external_integrations (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_id INTEGER NOT NULL,
                execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_status TEXT NOT NULL,
                records_processed INTEGER DEFAULT 0,
                records_success INTEGER DEFAULT 0,
                records_failed INTEGER DEFAULT 0,
                execution_time_seconds REAL,
                error_log TEXT,
                output_file_path TEXT,
                triggered_by TEXT,
                session_id TEXT,
                FOREIGN KEY (integration_id) REFERENCES external_integrations (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_output_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_id INTEGER NOT NULL,
                output_name TEXT NOT NULL,
                output_format TEXT NOT NULL,
                output_template TEXT,
                output_fields TEXT,
                file_naming_pattern TEXT,
                schedule_config TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (integration_id) REFERENCES external_integrations (id) ON DELETE CASCADE
            )
        ''')
        
        # LTL Tracking tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_history_id INTEGER NOT NULL,
                pro_number TEXT NOT NULL,
                carrier_name TEXT,
                load_id TEXT,
                request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (upload_history_id) REFERENCES upload_history (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_request_id INTEGER NOT NULL,
                tracking_status TEXT,
                tracking_location TEXT,
                tracking_event TEXT,
                tracking_timestamp TEXT,
                scraped_data TEXT,
                scrape_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scrape_success BOOLEAN DEFAULT 1,
                error_message TEXT,
                FOREIGN KEY (tracking_request_id) REFERENCES tracking_requests (id) ON DELETE CASCADE
            )
        ''')
        
        # Insert default integration types
        cursor.execute('''
            INSERT OR IGNORE INTO integration_types (type_name, type_display_name, description, default_config)
            VALUES 
                ('ltl_carrier', 'LTL Carrier', 'Integration with LTL carrier systems for rate quotes and tracking', '{"api_type": "rest", "auth_type": "bearer", "rate_limit": 100}'),
                ('freight_api', 'Freight API', 'Generic freight and logistics API integration', '{"api_type": "rest", "auth_type": "api_key", "rate_limit": 200}'),
                ('tracking_api', 'Tracking API', 'Shipment tracking and visibility API', '{"api_type": "rest", "auth_type": "oauth", "rate_limit": 500}'),
                ('pricing_api', 'Pricing API', 'Freight pricing and rate calculation API', '{"api_type": "rest", "auth_type": "bearer", "rate_limit": 100}'),
                ('customs_api', 'Customs API', 'Customs and border documentation API', '{"api_type": "rest", "auth_type": "certificate", "rate_limit": 50}'),
                ('warehouse_api', 'Warehouse API', 'Warehouse management system integration', '{"api_type": "rest", "auth_type": "basic", "rate_limit": 300}'),
                ('edi_integration', 'EDI Integration', 'Electronic Data Interchange for freight documents', '{"protocol": "edi", "standards": ["x12", "edifact"], "rate_limit": 1000}'),
                ('custom_integration', 'Custom Integration', 'Custom API or data source integration', '{"api_type": "configurable", "auth_type": "configurable", "rate_limit": 100}'),
                ('web_scraper', 'Web Scraper', 'Automated web scraping for carrier data extraction', '{"scraper_type": "web", "auth_type": "form_login", "rate_limit": 50, "delay_seconds": 5}')
        ''')
        
        conn.commit()
        
        # Migrate existing databases to new schema
        self._migrate_database_schema(conn, cursor)
        
        conn.commit()
        conn.close()
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, backup_name=None, description=""):
        """Create a complete database backup"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup directory
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.db")
        
        try:
            # Create database backup
            shutil.copy2(self.db_path, backup_path)
            
            # Calculate checksum for integrity verification
            checksum = self._calculate_file_checksum(backup_path)
            
            # Get backup size
            backup_size = os.path.getsize(backup_path)
            
            # Record backup in history
            self._save_backup_history(backup_name, backup_path, backup_size, "database", checksum, description)
            
            return {
                'success': True,
                'backup_name': backup_name,
                'backup_path': backup_path,
                'size': backup_size,
                'checksum': checksum
            }
            
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_data_export(self, customer_name=None, export_format="json", backup_name=None):
        """Export data in various formats (JSON, CSV)"""
        if not backup_name:
            backup_name = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            export_data = {
                'export_info': {
                    'created_at': datetime.now().isoformat(),
                    'export_format': export_format,
                    'customer_name': customer_name
                },
                'customer_mappings': [],
                'upload_history': []
            }
            
            # Export customer mappings
            if customer_name:
                mapping = self.get_customer_mapping(customer_name)
                if mapping:
                    export_data['customer_mappings'].append({
                        'customer_name': customer_name,
                        'field_mappings': mapping['field_mappings'],
                        # Don't export API credentials for security
                        'api_credentials': {'base_url': mapping['api_credentials'].get('base_url', '')},
                        'created_at': datetime.now().isoformat()
                    })
            else:
                # Export all mappings
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT customer_name, field_mappings, created_at, updated_at FROM customer_mappings')
                mappings = cursor.fetchall()
                
                for mapping in mappings:
                    export_data['customer_mappings'].append({
                        'customer_name': mapping[0],
                        'field_mappings': json.loads(mapping[1]),
                        'created_at': mapping[2],
                        'updated_at': mapping[3]
                    })
                conn.close()
            
            # Export upload history
            history = self.get_upload_history(customer_name, limit=None)
            for record in history:
                export_data['upload_history'].append({
                    'brokerage_name': record[1],  # Updated to use brokerage_name
                    'filename': record[3],        # Adjusted index for new schema
                    'total_records': record[4],
                    'successful_records': record[5],
                    'failed_records': record[6],
                    'error_log': json.loads(record[7]) if record[7] else None,
                    'upload_timestamp': record[10]  # Adjusted index for new schema
                })
            
            # Export learning data
            learning_data = self.export_learning_data()
            export_data['learning_data'] = learning_data
            
            # Save export file
            export_path = os.path.join(self.backup_dir, f"{backup_name}.json")
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            # Create ZIP archive
            zip_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(export_path, f"{backup_name}.json")
            
            # Clean up JSON file
            os.remove(export_path)
            
            # Calculate checksum
            checksum = self._calculate_file_checksum(zip_path)
            backup_size = os.path.getsize(zip_path)
            
            # Record export in history
            self._save_backup_history(backup_name, zip_path, backup_size, "export", checksum, f"Data export for {customer_name or 'all customers'}")
            
            return {
                'success': True,
                'export_name': backup_name,
                'export_path': zip_path,
                'size': backup_size,
                'checksum': checksum
            }
            
        except Exception as e:
            logging.error(f"Error creating data export: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def restore_from_backup(self, backup_name):
        """Restore database from backup"""
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.db")
        
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'error': 'Backup file not found'
            }
        
        try:
            # Verify backup integrity
            backup_info = self.get_backup_info(backup_name)
            if backup_info:
                current_checksum = self._calculate_file_checksum(backup_path)
                if current_checksum != backup_info['checksum']:
                    return {
                        'success': False,
                        'error': 'Backup file integrity check failed'
                    }
            
            # Create current database backup before restore
            current_backup = self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "Backup before restore operation")
            
            # Restore database
            shutil.copy2(backup_path, self.db_path)
            
            return {
                'success': True,
                'restored_from': backup_name,
                'pre_restore_backup': current_backup
            }
            
        except Exception as e:
            logging.error(f"Error restoring from backup: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def import_data(self, import_file_path):
        """Import data from export file"""
        try:
            # Extract and read import file
            with zipfile.ZipFile(import_file_path, 'r') as zipf:
                # Get the JSON file from the zip
                json_files = [f for f in zipf.namelist() if f.endswith('.json')]
                if not json_files:
                    return {'success': False, 'error': 'No JSON data file found in archive'}
                
                json_content = zipf.read(json_files[0])
                import_data = json.loads(json_content)
            
            # Validate import data structure
            if not all(key in import_data for key in ['export_info', 'customer_mappings', 'upload_history']):
                return {'success': False, 'error': 'Invalid import data structure'}
            
            # Import customer mappings
            imported_mappings = 0
            imported_history = 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Import customer mappings (skip API credentials for security)
                for mapping in import_data['customer_mappings']:
                    cursor.execute('''
                        INSERT OR IGNORE INTO customer_mappings 
                        (customer_name, field_mappings, api_credentials, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        mapping['customer_name'],
                        json.dumps(mapping['field_mappings']),
                        json.dumps({'base_url': '', 'api_key': ''}),  # Empty credentials
                        mapping.get('created_at', datetime.now().isoformat()),
                        mapping.get('updated_at', datetime.now().isoformat())
                    ))
                    imported_mappings += 1
                
                # Import upload history
                for record in import_data['upload_history']:
                    cursor.execute('''
                        INSERT INTO upload_history 
                        (brokerage_name, filename, total_records, successful_records, failed_records, error_log, upload_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record.get('brokerage_name', record.get('customer_name', 'Unknown')),  # Handle both old and new formats
                        record['filename'],
                        record['total_records'],
                        record['successful_records'],
                        record['failed_records'],
                        json.dumps(record['error_log']) if record['error_log'] else None,
                        record['upload_timestamp']
                    ))
                    imported_history += 1
                
                # Import learning data if present
                imported_learning = 0
                if 'learning_data' in import_data:
                    try:
                        self.import_learning_data(import_data['learning_data'])
                        imported_learning = 1
                    except Exception as e:
                        logging.error(f"Error importing learning data: {e}")
                
                conn.commit()
                
                return {
                    'success': True,
                    'imported_mappings': imported_mappings,
                    'imported_history': imported_history,
                    'imported_learning': imported_learning
                }
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Error importing data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_backup_list(self):
        """Get list of available backups"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT backup_name, backup_path, backup_size, backup_type, created_at, description
            FROM backup_history
            ORDER BY created_at DESC
        ''')
        
        backups = cursor.fetchall()
        conn.close()
        
        # Verify backup files still exist
        verified_backups = []
        for backup in backups:
            if os.path.exists(backup[1]):
                verified_backups.append({
                    'name': backup[0],
                    'path': backup[1],
                    'size': backup[2],
                    'type': backup[3],
                    'created_at': backup[4],
                    'description': backup[5]
                })
        
        return verified_backups

    def get_backup_info(self, backup_name):
        """Get detailed information about a specific backup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT backup_name, backup_path, backup_size, backup_type, checksum, created_at, description
            FROM backup_history
            WHERE backup_name = ?
        ''', (backup_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'name': result[0],
                'path': result[1],
                'size': result[2],
                'type': result[3],
                'checksum': result[4],
                'created_at': result[5],
                'description': result[6]
            }
        return None

    def delete_backup(self, backup_name):
        """Delete a backup file and its record"""
        backup_info = self.get_backup_info(backup_name)
        if not backup_info:
            return {'success': False, 'error': 'Backup not found'}
        
        try:
            # Delete backup file
            if os.path.exists(backup_info['path']):
                os.remove(backup_info['path'])
            
            # Remove from backup history
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM backup_history WHERE backup_name = ?', (backup_name,))
            conn.commit()
            conn.close()
            
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error deleting backup: {e}")
            return {'success': False, 'error': str(e)}

    def verify_backup_integrity(self, backup_name):
        """Verify the integrity of a backup file"""
        backup_info = self.get_backup_info(backup_name)
        if not backup_info:
            return {'success': False, 'error': 'Backup not found'}
        
        if not os.path.exists(backup_info['path']):
            return {'success': False, 'error': 'Backup file not found'}
        
        try:
            current_checksum = self._calculate_file_checksum(backup_info['path'])
            integrity_ok = current_checksum == backup_info['checksum']
            
            return {
                'success': True,
                'integrity_ok': integrity_ok,
                'original_checksum': backup_info['checksum'],
                'current_checksum': current_checksum
            }
            
        except Exception as e:
            logging.error(f"Error verifying backup integrity: {e}")
            return {'success': False, 'error': str(e)}

    def _save_backup_history(self, backup_name, backup_path, backup_size, backup_type, checksum, description):
        """Save backup record to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backup_history 
            (backup_name, backup_path, backup_size, backup_type, checksum, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (backup_name, backup_path, backup_size, backup_type, checksum, description))
        
        conn.commit()
        conn.close()

    def _calculate_file_checksum(self, file_path):
        """Calculate SHA256 checksum of a file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def get_database_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get table counts
        cursor.execute('SELECT COUNT(*) FROM customer_mappings')
        mapping_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM upload_history')
        history_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM backup_history')
        backup_count = cursor.fetchone()[0]
        
        # Get brokerage configurations count (primary table)
        cursor.execute('SELECT COUNT(*) FROM brokerage_configurations')
        brokerage_configs_count = cursor.fetchone()[0]
        
        # Get learning table counts
        cursor.execute('SELECT COUNT(*) FROM mapping_interactions')
        interactions_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM brokerage_patterns')
        patterns_count = cursor.fetchone()[0]
        
        # Get database size
        db_size = os.path.getsize(self.db_path)
        
        conn.close()
        
        return {
            'customer_mappings': mapping_count,
            'upload_history': history_count,
            'backup_history': backup_count,
            'brokerage_configurations': brokerage_configs_count,
            'mapping_interactions': interactions_count,
            'brokerage_patterns': patterns_count,
            'database_size': db_size
        }
    
    def save_customer_mapping(self, customer_name, field_mappings, api_credentials):
        """Save or update customer mapping configuration"""
        # Input validation
        if not customer_name or not isinstance(customer_name, str):
            raise ValueError("Invalid customer name")
        if len(customer_name) > 100:
            raise ValueError("Customer name too long")
        if not field_mappings or not isinstance(field_mappings, dict):
            raise ValueError("Invalid field mappings")
        if not api_credentials or not isinstance(api_credentials, dict):
            raise ValueError("Invalid API credentials")
        
        # Sanitize customer name
        import re
        safe_customer_name = re.sub(r'[^\w\s-]', '', customer_name.strip())[:100]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Encrypt API credentials
            key = self._get_encryption_key()
            f = Fernet(key)
            
            # Validate API credentials structure before encrypting
            required_cred_fields = ['base_url', 'api_key']
            if not all(field in api_credentials for field in required_cred_fields):
                raise ValueError("Missing required API credential fields")
            
            encrypted_credentials = f.encrypt(json.dumps(api_credentials).encode())
            
            cursor.execute('''
                INSERT OR REPLACE INTO customer_mappings 
                (customer_name, field_mappings, api_credentials, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (safe_customer_name, json.dumps(field_mappings), encrypted_credentials, datetime.now()))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Error saving customer mapping: {e}")
            raise
        finally:
            conn.close()
    
    def get_customer_mapping(self, customer_name):
        """Retrieve customer mapping configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT field_mappings, api_credentials FROM customer_mappings 
            WHERE customer_name = ?
        ''', (customer_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Decrypt API credentials
            key = self._get_encryption_key()
            f = Fernet(key)
            decrypted_credentials = json.loads(f.decrypt(result[1]).decode())
            
            return {
                'field_mappings': json.loads(result[0]),
                'api_credentials': decrypted_credentials
            }
        return None
    
    def delete_customer_mapping(self, customer_name):
        """Delete customer mapping configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM customer_mappings WHERE customer_name = ?
        ''', (customer_name,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def get_customer_mapping_details(self, customer_name):
        """Get customer mapping metadata (creation/update times, field count, etc.)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT created_at, updated_at, field_mappings FROM customer_mappings 
            WHERE customer_name = ?
        ''', (customer_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            field_mappings = json.loads(result[2])
            return {
                'created_at': result[0],
                'updated_at': result[1],
                'field_count': len(field_mappings),
                'fields': list(field_mappings.keys())
            }
        return None
    
    def save_upload_history(self, brokerage_name, filename, total_records, successful_records, failed_records, error_log):
        """Save upload history record - legacy method updated to use brokerage_name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO upload_history 
            (brokerage_name, filename, total_records, successful_records, failed_records, error_log)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (brokerage_name, filename, total_records, successful_records, failed_records, error_log))
        
        conn.commit()
        conn.close()
    
    def get_upload_history(self, brokerage_name=None, limit: Optional[int] = 50):
        """Retrieve upload history - legacy method updated to use brokerage_name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if brokerage_name:
            if limit is None:
                cursor.execute('''
                    SELECT * FROM upload_history 
                    WHERE brokerage_name = ?
                    ORDER BY upload_timestamp DESC
                ''', (brokerage_name,))
            else:
                cursor.execute('''
                    SELECT * FROM upload_history 
                    WHERE brokerage_name = ?
                    ORDER BY upload_timestamp DESC
                    LIMIT ?
                ''', (brokerage_name, limit))
        else:
            if limit is None:
                cursor.execute('''
                    SELECT * FROM upload_history 
                    ORDER BY upload_timestamp DESC
                ''')
            else:
                cursor.execute('''
                    SELECT * FROM upload_history 
                    ORDER BY upload_timestamp DESC
                    LIMIT ?
                ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def _get_encryption_key(self):
        """Get or create encryption key for API credentials"""
        # Try to get key from Streamlit secrets first (for cloud deployment)
        try:
            import streamlit as st
            if 'database' in st.secrets and 'ENCRYPTION_KEY' in st.secrets.database:
                key = st.secrets.database.ENCRYPTION_KEY.encode()
                # Validate the key is the correct format
                if len(key) == 44:  # Fernet key length
                    return key
                else:
                    logging.warning("Invalid encryption key format in secrets")
        except Exception:
            # Streamlit secrets not available or not configured
            pass
        
        # Fall back to local file for development
        key_file = "config/encryption.key"
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    key = f.read()
                # Validate the key is the correct format
                if len(key) == 44:  # Fernet key length
                    return key
                else:
                    logging.warning("Invalid encryption key format, generating new key")
            except Exception as e:
                logging.error(f"Error reading encryption key: {e}")
        
        # Generate new key
        key = Fernet.generate_key()
        os.makedirs("config", exist_ok=True)
        try:
            # Write with restricted permissions
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set file permissions to owner-only (Unix-like systems)
            try:
                import stat
                os.chmod(key_file, stat.S_IRUSR | stat.S_IWUSR)
            except:
                pass  # Windows or permission error
        except Exception as e:
            logging.error(f"Error writing encryption key: {e}")
            raise
        return key 

    def _encrypt_credentials(self, credentials_json):
        """Encrypt credentials JSON string"""
        try:
            key = self._get_encryption_key()
            if not key:
                raise ValueError("Encryption key not available")
            
            f = Fernet(key)
            return f.encrypt(credentials_json.encode())
        except Exception as e:
            logging.error(f"Error encrypting credentials: {e}")
            raise

    def _decrypt_credentials(self, encrypted_credentials):
        """Decrypt credentials and return as dictionary"""
        try:
            key = self._get_encryption_key()
            if not key:
                raise ValueError("Encryption key not available")
            
            f = Fernet(key)
            decrypted_json = f.decrypt(encrypted_credentials).decode()
            return json.loads(decrypted_json)
        except Exception as e:
            logging.warning(f"Could not decrypt credentials: {e}")
            return {}

    def save_brokerage_configuration(self, brokerage_name, configuration_name, field_mappings, api_credentials, file_headers=None, description=None):
        """Save brokerage-specific configuration with robust error handling"""
        # Input validation
        if not isinstance(brokerage_name, str) or not brokerage_name.strip():
            raise ValueError("Brokerage name must be a non-empty string")
        if not isinstance(configuration_name, str) or not configuration_name.strip():
            raise ValueError("Configuration name must be a non-empty string")
        if not isinstance(field_mappings, dict):
            raise ValueError("Field mappings must be a dictionary")
        if not isinstance(api_credentials, dict):
            raise ValueError("API credentials must be a dictionary")
        
        # Sanitize names
        import re
        safe_brokerage_name = re.sub(r'[^\w\s-]', '', brokerage_name.strip())[:100]
        safe_configuration_name = re.sub(r'[^\w\s-]', '', configuration_name.strip())[:100]
        
        # Validate API credentials structure
        required_fields = ['api_key', 'api_endpoint', 'api_secret', 'api_username']
        if not any(field in api_credentials for field in required_fields):
            raise ValueError("API credentials must contain at least one of: api_key, api_endpoint, api_secret, api_username")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Encrypt API credentials
            key = self._get_encryption_key()
            f = Fernet(key)
            
            # Validate API credentials structure before encrypting
            if not isinstance(api_credentials, dict):
                raise ValueError("API credentials must be a dictionary")
            
            encrypted_credentials = f.encrypt(json.dumps(api_credentials).encode())
            
            # Check if configuration already exists
            cursor.execute('''
                SELECT id FROM brokerage_configurations 
                WHERE brokerage_name = ? AND configuration_name = ?
            ''', (safe_brokerage_name, safe_configuration_name))
            
            existing_config = cursor.fetchone()
            
            if existing_config:
                # Update existing configuration
                config_id = existing_config[0]
                cursor.execute('''
                    UPDATE brokerage_configurations 
                    SET field_mappings = ?, api_credentials = ?, file_headers = ?, 
                        description = ?, updated_at = ?, last_used_at = ?
                    WHERE id = ?
                ''', (
                    json.dumps(field_mappings), encrypted_credentials,
                    json.dumps(file_headers) if file_headers else None,
                    description, datetime.now(), datetime.now(), config_id
                ))
                
                # Log the update
                self._log_configuration_change(
                    cursor, config_id, "UPDATE", 
                    f"Configuration '{safe_configuration_name}' updated",
                    None, None
                )
            else:
                # Create new configuration
                cursor.execute('''
                    INSERT INTO brokerage_configurations 
                    (brokerage_name, configuration_name, field_mappings, api_credentials, 
                     file_headers, description, last_used_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    safe_brokerage_name, safe_configuration_name, 
                    json.dumps(field_mappings), encrypted_credentials,
                    json.dumps(file_headers) if file_headers else None,
                    description, datetime.now()
                ))
                
                config_id = cursor.lastrowid
                
                # Log the creation
                self._log_configuration_change(
                    cursor, config_id, "CREATE", 
                    f"Configuration '{safe_configuration_name}' created",
                    None, None
                )
            
            conn.commit()
            return config_id
        
        except Exception as e:
            conn.rollback()
            logging.error(f"Error saving brokerage configuration: {e}")
            raise
        finally:
            conn.close()

    def get_brokerage_configurations(self, brokerage_name):
        """Get all configurations for a brokerage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, configuration_name, created_at, updated_at, last_used_at, 
                   version, description, field_mappings, api_credentials
            FROM brokerage_configurations 
            WHERE brokerage_name = ? AND is_active = 1
            ORDER BY last_used_at DESC, updated_at DESC
        ''', (brokerage_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        configurations = []
        for row in results:
            config_id, config_name, created_at, updated_at, last_used_at, version, desc, mappings, creds = row
            
            # Decrypt API credentials
            key = self._get_encryption_key()
            f = Fernet(key)
            decrypted_credentials = json.loads(f.decrypt(creds).decode())
            
            configurations.append({
                'id': config_id,
                'name': config_name,
                'created_at': created_at,
                'updated_at': updated_at,
                'last_used_at': last_used_at,
                'version': version,
                'description': desc,
                'field_mappings': json.loads(mappings),
                'api_credentials': decrypted_credentials,
                'field_count': len(json.loads(mappings))
            })
        
        return configurations

    def get_brokerage_configuration(self, brokerage_name, configuration_name):
        """Get specific brokerage configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT field_mappings, api_credentials, file_headers, version, description
            FROM brokerage_configurations 
            WHERE brokerage_name = ? AND configuration_name = ? AND is_active = 1
        ''', (brokerage_name, configuration_name))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            mappings, creds, headers, version, desc = result
            
            # Decrypt API credentials
            key = self._get_encryption_key()
            f = Fernet(key)
            decrypted_credentials = json.loads(f.decrypt(creds).decode())
            
            return {
                'field_mappings': json.loads(mappings),
                'api_credentials': decrypted_credentials,
                'file_headers': json.loads(headers) if headers else None,
                'version': version,
                'description': desc
            }
        return None

    def update_configuration_last_used(self, brokerage_name, configuration_name):
        """Update the last used timestamp for a configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE brokerage_configurations 
            SET last_used_at = ?
            WHERE brokerage_name = ? AND configuration_name = ?
        ''', (datetime.now(), brokerage_name, configuration_name))
        
        conn.commit()
        conn.close()

    def get_all_brokerages(self):
        """Get list of all brokerages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT brokerage_name, COUNT(*) as config_count,
                   MAX(last_used_at) as last_used
            FROM brokerage_configurations 
            WHERE is_active = 1
            GROUP BY brokerage_name
            ORDER BY last_used DESC, brokerage_name
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [{'name': row[0], 'config_count': row[1], 'last_used': row[2]} for row in results]

    def save_upload_history_enhanced(self, brokerage_name, configuration_name, filename, 
                                   total_records, successful_records, failed_records, 
                                   error_log, processing_time, file_headers, session_id):
        """Save enhanced upload history with detailed error tracking"""
        
        # Data validation and type conversion to prevent SQLite parameter binding errors
        def safe_convert_to_str(value, default=""):
            """Safely convert value to string"""
            if value is None:
                return default
            if isinstance(value, (str, int, float)):
                return str(value)
            return default
        
        def safe_convert_to_int(value, default=0):
            """Safely convert value to integer"""
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                try:
                    return int(float(value))
                except (ValueError, TypeError):
                    return default
            if isinstance(value, dict):
                # Handle case where value is accidentally a dict - extract meaningful value if possible
                if 'value' in value:
                    return safe_convert_to_int(value['value'], default)
                return default
            return default
        
        def safe_convert_to_float(value, default=0.0):
            """Safely convert value to float"""
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            return default
        
        # Validate and convert all parameters
        brokerage_name = safe_convert_to_str(brokerage_name, "Unknown")
        configuration_name = safe_convert_to_str(configuration_name, "Unknown")
        filename = safe_convert_to_str(filename, "unknown_file.csv")
        total_records = safe_convert_to_int(total_records, 0)
        successful_records = safe_convert_to_int(successful_records, 0)
        failed_records = safe_convert_to_int(failed_records, 0)
        processing_time = safe_convert_to_float(processing_time, 0.0)
        session_id = safe_convert_to_str(session_id, f"session_{datetime.now().isoformat()}")
        
        # Validate integer constraints
        if total_records < 0:
            total_records = 0
        if successful_records < 0:
            successful_records = 0
        if failed_records < 0:
            failed_records = 0
        if processing_time < 0:
            processing_time = 0.0
        
        # Ensure successful + failed doesn't exceed total (logical consistency)
        if successful_records + failed_records > total_records:
            total_records = successful_records + failed_records
        
        # Handle error_log - ensure it's a string (JSON) or None
        if error_log is not None and not isinstance(error_log, str):
            try:
                error_log = json.dumps(error_log)
            except:
                error_log = None
        
        # Handle file_headers - ensure it's properly JSON serialized
        if file_headers is not None:
            try:
                if isinstance(file_headers, str):
                    # Already a string, validate it's valid JSON
                    json.loads(file_headers)
                else:
                    # Convert to JSON string
                    file_headers = json.dumps(file_headers)
            except:
                file_headers = None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO upload_history 
            (brokerage_name, configuration_name, filename, total_records, 
             successful_records, failed_records, error_log, processing_time_seconds,
             file_headers, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            brokerage_name, configuration_name, filename, total_records,
            successful_records, failed_records, error_log, processing_time,
            file_headers, session_id
        ))
        
        upload_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return upload_id

    def save_processing_errors(self, upload_history_id, errors_list):
        """Save detailed processing errors for troubleshooting"""
        
        # Validate upload_history_id
        if not isinstance(upload_history_id, int) or upload_history_id <= 0:
            logging.error(f"Invalid upload_history_id: {upload_history_id}")
            return
        
        # Validate errors_list
        if not errors_list or not isinstance(errors_list, list):
            logging.warning("No errors provided or invalid errors_list format")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        def safe_convert_to_str(value, default=""):
            """Safely convert value to string"""
            if value is None:
                return default
            if isinstance(value, (str, int, float)):
                return str(value)
            if isinstance(value, dict):
                return str(value)
            return default
        
        def safe_convert_to_int(value, default=None):
            """Safely convert value to integer"""
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                try:
                    return int(float(value))
                except (ValueError, TypeError):
                    return default
            return default
        
        for error in errors_list:
            # Validate that error is a dictionary
            if not isinstance(error, dict):
                logging.warning(f"Skipping invalid error record: {error}")
                continue
            
            # Extract and validate error fields
            row_number = safe_convert_to_int(error.get('row_number'))
            field_name = safe_convert_to_str(error.get('field_name'))
            error_type = safe_convert_to_str(error.get('error_type'))
            error_message = safe_convert_to_str(error.get('error_message'))
            suggested_fix = safe_convert_to_str(error.get('suggested_fix'))
            original_value = safe_convert_to_str(error.get('original_value'))
            expected_format = safe_convert_to_str(error.get('expected_format'))
            
            # Skip if essential fields are missing
            if not error_type or not error_message:
                logging.warning(f"Skipping error record with missing essential fields: {error}")
                continue
            
            cursor.execute('''
                INSERT INTO processing_errors 
                (upload_history_id, row_number, field_name, error_type, 
                 error_message, suggested_fix, original_value, expected_format)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                upload_history_id,
                row_number,
                field_name,
                error_type,
                error_message,
                suggested_fix,
                original_value,
                expected_format
            ))
        
        conn.commit()
        conn.close()

    def get_brokerage_upload_history(self, brokerage_name, limit=50):
        """Get upload history for a specific brokerage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT h.*, COUNT(e.id) as error_count
            FROM upload_history h
            LEFT JOIN processing_errors e ON h.id = e.upload_history_id
            WHERE h.brokerage_name = ?
            GROUP BY h.id
            ORDER BY h.upload_timestamp DESC
            LIMIT ?
        ''', (brokerage_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return results

    def _log_configuration_change(self, cursor, config_id, change_type, description, old_value, new_value):
        """Log configuration changes for version tracking"""
        cursor.execute('''
            INSERT INTO configuration_changes 
            (configuration_id, change_type, change_description, old_value, new_value)
            VALUES (?, ?, ?, ?, ?)
        ''', (config_id, change_type, description, old_value, new_value))

    def compare_file_headers(self, saved_headers, current_headers):
        """Compare saved configuration headers with current file headers"""
        if not saved_headers:
            return {'status': 'new_config', 'changes': [], 'missing': [], 'added': current_headers}
        
        saved_set = set(saved_headers)
        current_set = set(current_headers)
        
        missing = list(saved_set - current_set)  # In saved but not in current
        added = list(current_set - saved_set)    # In current but not in saved
        common = list(saved_set & current_set)   # In both
        
        status = 'identical' if not missing and not added else 'changed'
        
        return {
            'status': status,
            'missing': missing,
            'added': added,
            'common': common,
            'changes': missing + added
        } 

    def _migrate_database_schema(self, conn, cursor):
        """Migrate database schema from old format to new format"""
        try:
            # Check if upload_history table has old schema (customer_name instead of brokerage_name)
            cursor.execute("PRAGMA table_info(upload_history)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'customer_name' in column_names and 'brokerage_name' not in column_names:
                logging.info("Migrating upload_history table from customer_name to brokerage_name schema...")
                
                # Create new table with correct schema
                cursor.execute('''
                    CREATE TABLE upload_history_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        brokerage_name TEXT NOT NULL,
                        configuration_name TEXT,
                        filename TEXT NOT NULL,
                        total_records INTEGER,
                        successful_records INTEGER,
                        failed_records INTEGER,
                        error_log TEXT,
                        processing_time_seconds REAL,
                        file_headers TEXT,
                        upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_id TEXT
                    )
                ''')
                
                # Copy data from old table to new table (customer_name -> brokerage_name)
                cursor.execute('''
                    INSERT INTO upload_history_new 
                    (id, brokerage_name, filename, total_records, successful_records, 
                     failed_records, error_log, upload_timestamp)
                    SELECT id, customer_name, filename, total_records, successful_records,
                           failed_records, error_log, upload_timestamp
                    FROM upload_history
                ''')
                
                # Drop old table and rename new table
                cursor.execute('DROP TABLE upload_history')
                cursor.execute('ALTER TABLE upload_history_new RENAME TO upload_history')
                
                logging.info("Successfully migrated upload_history table schema")
                
        except Exception as e:
            logging.error(f"Error during database migration: {e}")
            # Don't raise error - let the app continue with what it has 
            
    # =============================================================================
    # Learning System Methods
    # =============================================================================
    
    def save_mapping_interaction(self, interaction_data):
        """Save mapping interaction data for learning system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert mapping interaction
            cursor.execute('''
                INSERT INTO mapping_interactions 
                (session_id, brokerage_name, configuration_name, file_headers, 
                 suggested_mappings, final_mappings, suggestions_accepted, 
                 manual_corrections, total_fields, processing_success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                interaction_data.get('session_id'),
                interaction_data.get('brokerage_name'),
                interaction_data.get('configuration_name'),
                json.dumps(interaction_data.get('file_headers', [])),
                json.dumps(interaction_data.get('suggested_mappings', {})),
                json.dumps(interaction_data.get('final_mappings', {})),
                interaction_data.get('suggestions_accepted', 0),
                interaction_data.get('manual_corrections', 0),
                interaction_data.get('total_fields', 0),
                interaction_data.get('processing_success_rate', 0.0)
            ))
            
            interaction_id = cursor.lastrowid
            
            # Insert individual mapping decisions
            decisions = interaction_data.get('decisions', [])
            for decision in decisions:
                cursor.execute('''
                    INSERT INTO mapping_decisions 
                    (interaction_id, column_name, column_sample_data, column_data_type,
                     suggested_field, suggested_confidence, actual_field, decision_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction_id,
                    decision.get('column_name'),
                    json.dumps(decision.get('column_sample_data', [])),
                    decision.get('column_data_type'),
                    decision.get('suggested_field'),
                    decision.get('suggested_confidence', 0.0),
                    decision.get('actual_field'),
                    decision.get('decision_type')
                ))
            
            conn.commit()
            return interaction_id
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error saving mapping interaction: {e}")
            raise
        finally:
            conn.close()
    
    def update_brokerage_patterns(self, brokerage_name, mapping_decisions):
        """Update brokerage-specific mapping patterns based on user decisions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for decision in mapping_decisions:
                column_name = decision.get('column_name')
                actual_field = decision.get('actual_field')
                decision_type = decision.get('decision_type')
                
                if not column_name or not actual_field:
                    continue
                
                # Normalize column name for pattern matching
                column_pattern = self._normalize_column_name(column_name)
                
                # Get current pattern stats
                cursor.execute('''
                    SELECT success_count, total_count, average_confidence
                    FROM brokerage_patterns
                    WHERE brokerage_name = ? AND column_pattern = ? AND api_field = ?
                ''', (brokerage_name, column_pattern, actual_field))
                
                result = cursor.fetchone()
                
                if result:
                    # Update existing pattern
                    success_count, total_count, avg_confidence = result
                    
                    # Update counts
                    if decision_type == 'accepted':
                        success_count += 1
                    total_count += 1
                    
                    # Update average confidence
                    new_confidence = decision.get('suggested_confidence', 0.0)
                    if total_count > 0:
                        avg_confidence = ((avg_confidence * (total_count - 1)) + new_confidence) / total_count
                    
                    cursor.execute('''
                        UPDATE brokerage_patterns
                        SET success_count = ?, total_count = ?, average_confidence = ?,
                            last_updated = ?, sample_values = ?
                        WHERE brokerage_name = ? AND column_pattern = ? AND api_field = ?
                    ''', (
                        success_count, total_count, avg_confidence, datetime.now(),
                        json.dumps(decision.get('column_sample_data', [])),
                        brokerage_name, column_pattern, actual_field
                    ))
                    
                else:
                    # Create new pattern
                    success_count = 1 if decision_type == 'accepted' else 0
                    confidence = decision.get('suggested_confidence', 0.0)
                    
                    cursor.execute('''
                        INSERT INTO brokerage_patterns
                        (brokerage_name, column_pattern, api_field, success_count, total_count,
                         average_confidence, data_type_pattern, sample_values)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        brokerage_name, column_pattern, actual_field, success_count, 1,
                        confidence, decision.get('column_data_type'),
                        json.dumps(decision.get('column_sample_data', []))
                    ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error updating brokerage patterns: {e}")
            raise
        finally:
            conn.close()
    
    def get_brokerage_patterns(self, brokerage_name, column_pattern=None):
        """Get learning patterns for a specific brokerage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if column_pattern:
            cursor.execute('''
                SELECT column_pattern, api_field, success_count, total_count,
                       average_confidence, data_type_pattern, sample_values
                FROM brokerage_patterns
                WHERE brokerage_name = ? AND column_pattern = ?
                ORDER BY success_count DESC, average_confidence DESC
            ''', (brokerage_name, column_pattern))
        else:
            cursor.execute('''
                SELECT column_pattern, api_field, success_count, total_count,
                       average_confidence, data_type_pattern, sample_values
                FROM brokerage_patterns
                WHERE brokerage_name = ?
                ORDER BY success_count DESC, average_confidence DESC
            ''', (brokerage_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in results:
            pattern = {
                'column_pattern': row[0],
                'api_field': row[1],
                'success_count': row[2],
                'total_count': row[3],
                'average_confidence': row[4],
                'data_type_pattern': row[5],
                'sample_values': json.loads(row[6]) if row[6] else []
            }
            patterns.append(pattern)
        
        return patterns
    
    def get_learning_suggestions(self, brokerage_name, column_name, sample_data=None):
        """Get mapping suggestions based on learned patterns"""
        normalized_column = self._normalize_column_name(column_name)
        patterns = self.get_brokerage_patterns(brokerage_name, normalized_column)
        
        suggestions = []
        for pattern in patterns:
            if pattern['total_count'] >= 2:  # Minimum threshold for confidence
                # Calculate confidence based on success rate and historical confidence
                success_rate = pattern['success_count'] / pattern['total_count']
                historical_confidence = pattern['average_confidence']
                
                # Weighted confidence calculation
                learned_confidence = (success_rate * 0.6) + (historical_confidence * 0.4)
                
                suggestions.append({
                    'api_field': pattern['api_field'],
                    'confidence': learned_confidence,
                    'source': 'learning',
                    'success_rate': success_rate,
                    'sample_count': pattern['total_count']
                })
        
        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)
    
    def get_mapping_analytics(self, brokerage_name, days_back=30):
        """Get analytics on mapping patterns and learning progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent interactions
        cursor.execute('''
            SELECT COUNT(*) as total_interactions,
                   AVG(suggestions_accepted) as avg_suggestions_accepted,
                   AVG(manual_corrections) as avg_manual_corrections,
                   AVG(processing_success_rate) as avg_processing_success
            FROM mapping_interactions
            WHERE brokerage_name = ?
            AND timestamp >= datetime('now', '-{} days')
        '''.format(days_back), (brokerage_name,))
        
        interaction_stats = cursor.fetchone()
        
        # Get top patterns
        cursor.execute('''
            SELECT api_field, COUNT(*) as usage_count,
                   AVG(average_confidence) as avg_confidence
            FROM brokerage_patterns
            WHERE brokerage_name = ?
            GROUP BY api_field
            ORDER BY usage_count DESC
            LIMIT 10
        ''', (brokerage_name,))
        
        top_patterns = cursor.fetchall()
        
        # Get learning progress (improvement over time)
        cursor.execute('''
            SELECT DATE(timestamp) as date,
                   AVG(suggestions_accepted) as daily_acceptance_rate
            FROM mapping_interactions
            WHERE brokerage_name = ?
            AND timestamp >= datetime('now', '-{} days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        '''.format(days_back), (brokerage_name,))
        
        learning_progress = cursor.fetchall()
        
        conn.close()
        
        return {
            'interaction_stats': {
                'total_interactions': interaction_stats[0] if interaction_stats[0] else 0,
                'avg_suggestions_accepted': interaction_stats[1] if interaction_stats[1] else 0,
                'avg_manual_corrections': interaction_stats[2] if interaction_stats[2] else 0,
                'avg_processing_success': interaction_stats[3] if interaction_stats[3] else 0
            },
            'top_patterns': [
                {
                    'api_field': pattern[0],
                    'usage_count': pattern[1],
                    'avg_confidence': pattern[2]
                }
                for pattern in top_patterns
            ],
            'learning_progress': [
                {
                    'date': progress[0],
                    'acceptance_rate': progress[1]
                }
                for progress in learning_progress
            ]
        }
    
    def _normalize_column_name(self, column_name):
        """Normalize column name for pattern matching"""
        import re
        
        # Convert to lowercase and replace common separators
        normalized = column_name.lower()
        normalized = re.sub(r'[_\-\s]+', '_', normalized)
        normalized = re.sub(r'[^\w_]', '', normalized)
        normalized = normalized.strip('_')
        
        return normalized
    
    def cleanup_old_learning_data(self, days_to_keep=90):
        """Clean up old learning data to prevent database bloat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clean up old interactions
            cursor.execute('''
                DELETE FROM mapping_interactions
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            # Clean up orphaned decisions
            cursor.execute('''
                DELETE FROM mapping_decisions
                WHERE interaction_id NOT IN (
                    SELECT id FROM mapping_interactions
                )
            ''')
            
            # Clean up patterns with very low success rates and old data
            cursor.execute('''
                DELETE FROM brokerage_patterns
                WHERE (success_count = 0 AND total_count >= 5)
                OR last_updated < datetime('now', '-{} days')
            '''.format(days_to_keep * 2))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error cleaning up learning data: {e}")
            raise
        finally:
            conn.close()
    
    def export_learning_data(self):
        """Export learning data for backup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        learning_data = {
            'mapping_interactions': [],
            'mapping_decisions': [],
            'brokerage_patterns': []
        }
        
        # Export interactions
        cursor.execute('SELECT * FROM mapping_interactions')
        interactions = cursor.fetchall()
        
        interaction_columns = [desc[0] for desc in cursor.description]
        for interaction in interactions:
            learning_data['mapping_interactions'].append(
                dict(zip(interaction_columns, interaction))
            )
        
        # Export decisions
        cursor.execute('SELECT * FROM mapping_decisions')
        decisions = cursor.fetchall()
        
        decision_columns = [desc[0] for desc in cursor.description]
        for decision in decisions:
            learning_data['mapping_decisions'].append(
                dict(zip(decision_columns, decision))
            )
        
        # Export patterns
        cursor.execute('SELECT * FROM brokerage_patterns')
        patterns = cursor.fetchall()
        
        pattern_columns = [desc[0] for desc in cursor.description]
        for pattern in patterns:
            learning_data['brokerage_patterns'].append(
                dict(zip(pattern_columns, pattern))
            )
        
        conn.close()
        return learning_data
    
    def import_learning_data(self, learning_data):
        """Import learning data from backup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Import interactions
            for interaction in learning_data.get('mapping_interactions', []):
                cursor.execute('''
                    INSERT OR REPLACE INTO mapping_interactions
                    (id, session_id, brokerage_name, configuration_name, timestamp,
                     file_headers, suggested_mappings, final_mappings, suggestions_accepted,
                     manual_corrections, processing_success_rate, total_fields, user_satisfaction)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.get('id'),
                    interaction.get('session_id'),
                    interaction.get('brokerage_name'),
                    interaction.get('configuration_name'),
                    interaction.get('timestamp'),
                    interaction.get('file_headers'),
                    interaction.get('suggested_mappings'),
                    interaction.get('final_mappings'),
                    interaction.get('suggestions_accepted'),
                    interaction.get('manual_corrections'),
                    interaction.get('processing_success_rate'),
                    interaction.get('total_fields'),
                    interaction.get('user_satisfaction')
                ))
            
            # Import decisions
            for decision in learning_data.get('mapping_decisions', []):
                cursor.execute('''
                    INSERT OR REPLACE INTO mapping_decisions
                    (interaction_id, column_name, column_sample_data, column_data_type,
                     suggested_field, suggested_confidence, actual_field, decision_type,
                     decision_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    decision.get('interaction_id'),
                    decision.get('column_name'),
                    decision.get('column_sample_data'),
                    decision.get('column_data_type'),
                    decision.get('suggested_field'),
                    decision.get('suggested_confidence'),
                    decision.get('actual_field'),
                    decision.get('decision_type'),
                    decision.get('decision_timestamp')
                ))
            
            # Import patterns
            for pattern in learning_data.get('brokerage_patterns', []):
                cursor.execute('''
                    INSERT OR REPLACE INTO brokerage_patterns
                    (brokerage_name, column_pattern, api_field, success_count,
                     total_count, average_confidence, data_type_pattern,
                     sample_values, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern.get('brokerage_name'),
                    pattern.get('column_pattern'),
                    pattern.get('api_field'),
                    pattern.get('success_count'),
                    pattern.get('total_count'),
                    pattern.get('average_confidence'),
                    pattern.get('data_type_pattern'),
                    pattern.get('sample_values'),
                    pattern.get('last_updated')
                ))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error importing learning data: {e}")
            return False
        finally:
            conn.close()

    # =============================================================================
    # External Integrations Management
    # =============================================================================
    
    def get_integration_types(self):
        """Get all available integration types"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, type_name, type_display_name, description, default_config, is_active
            FROM integration_types
            WHERE is_active = 1
            ORDER BY type_display_name
        ''')
        
        types = []
        for row in cursor.fetchall():
            types.append({
                'id': row[0],
                'type_name': row[1],
                'type_display_name': row[2],
                'description': row[3],
                'default_config': row[4],
                'is_active': row[5]
            })
        
        conn.close()
        return types

    def save_integration_type(self, type_name, type_display_name, description, default_config=None):
        """Save a new integration type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO integration_types (type_name, type_display_name, description, default_config)
                VALUES (?, ?, ?, ?)
            ''', (type_name, type_display_name, description, default_config))
            
            integration_type_id = cursor.lastrowid
            conn.commit()
            
            logging.info(f"Integration type '{type_name}' saved successfully")
            return integration_type_id
            
        except sqlite3.IntegrityError:
            logging.warning(f"Integration type '{type_name}' already exists")
            # Get existing type ID
            cursor.execute('''
                SELECT id FROM integration_types WHERE type_name = ?
            ''', (type_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Error saving integration type: {e}")
            return None
        finally:
            conn.close()

    def save_external_integration(self, brokerage_name, integration_name, integration_type_id, 
                                config_data, auth_credentials=None, description=None, created_by=None):
        """Save external integration configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Convert config_data to JSON string
            config_json = json.dumps(config_data)
            
            # Encrypt auth credentials if provided
            auth_json = None
            if auth_credentials:
                auth_json = self._encrypt_credentials(json.dumps(auth_credentials))
            
            cursor.execute('''
                INSERT OR REPLACE INTO external_integrations 
                (brokerage_name, integration_name, integration_type_id, description, config_data, 
                 auth_credentials, created_by, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (brokerage_name, integration_name, integration_type_id, description, 
                  config_json, auth_json, created_by))
            
            integration_id = cursor.lastrowid
            conn.commit()
            
            logging.info(f"External integration '{integration_name}' saved for brokerage '{brokerage_name}'")
            return integration_id
            
        except sqlite3.IntegrityError as e:
            logging.warning(f"Duplicate integration name: {e}")
            # Update existing integration
            cursor.execute('''
                UPDATE external_integrations 
                SET integration_type_id = ?, description = ?, config_data = ?, 
                    auth_credentials = ?, updated_at = CURRENT_TIMESTAMP
                WHERE brokerage_name = ? AND integration_name = ?
            ''', (integration_type_id, description, config_json, auth_json, 
                  brokerage_name, integration_name))
            
            # Get the existing integration ID
            cursor.execute('''
                SELECT id FROM external_integrations 
                WHERE brokerage_name = ? AND integration_name = ?
            ''', (brokerage_name, integration_name))
            
            result = cursor.fetchone()
            integration_id = result[0] if result else None
            
            conn.commit()
            return integration_id
            
        except Exception as e:
            logging.error(f"Error saving external integration: {e}")
            return None
        finally:
            conn.close()

    def get_external_integrations(self, brokerage_name):
        """Get all external integrations for a brokerage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ei.id, ei.brokerage_name, ei.integration_name, ei.integration_type_id,
                   ei.description, ei.config_data, ei.auth_credentials, ei.is_active,
                   ei.created_at, ei.updated_at, ei.last_used_at, ei.created_by,
                   it.type_name, it.type_display_name, it.description as type_description
            FROM external_integrations ei
            JOIN integration_types it ON ei.integration_type_id = it.id
            WHERE ei.brokerage_name = ? AND ei.is_active = 1
            ORDER BY ei.integration_name
        ''', (brokerage_name,))
        
        integrations = []
        for row in cursor.fetchall():
            config_data = json.loads(row[5]) if row[5] else {}
            auth_credentials = self._decrypt_credentials(row[6]) if row[6] else {}
            
            integrations.append({
                'id': row[0],
                'brokerage_name': row[1],
                'name': row[2],
                'integration_type_id': row[3],
                'description': row[4],
                'config_data': config_data,
                'auth_credentials': auth_credentials,
                'is_active': row[7],
                'created_at': row[8],
                'updated_at': row[9],
                'last_used_at': row[10],
                'created_by': row[11],
                'type_name': row[12],
                'type_display_name': row[13],
                'type_description': row[14]
            })
        
        conn.close()
        return integrations
    
    def get_external_integration(self, integration_id):
        """Get a specific external integration by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ei.id, ei.brokerage_name, ei.integration_name, ei.description, 
                   ei.config_data, ei.auth_credentials, ei.is_active, ei.created_at, 
                   ei.updated_at, ei.last_used_at, ei.created_by,
                   it.type_name, it.type_display_name, it.description as type_description
            FROM external_integrations ei
            JOIN integration_types it ON ei.integration_type_id = it.id
            WHERE ei.id = ?
        ''', (integration_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            integration_id, brokerage_name, name, desc, config, creds, is_active, created, updated, last_used, created_by, type_name, type_display, type_desc = result
            
            # Decrypt auth credentials if present
            decrypted_credentials = None
            if creds:
                try:
                    key = self._get_encryption_key()
                    f = Fernet(key)
                    decrypted_credentials = json.loads(f.decrypt(creds).decode())
                except Exception as e:
                    logging.warning(f"Could not decrypt credentials for integration {name}: {e}")
            
            return {
                'id': integration_id,
                'brokerage_name': brokerage_name,
                'name': name,
                'description': desc,
                'config_data': json.loads(config),
                'auth_credentials': decrypted_credentials,
                'is_active': is_active,
                'created_at': created,
                'updated_at': updated,
                'last_used_at': last_used,
                'created_by': created_by,
                'type_name': type_name,
                'type_display_name': type_display,
                'type_description': type_desc
            }
        
        return None
    
    def delete_external_integration(self, integration_id):
        """Delete an external integration (soft delete)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE external_integrations 
            SET is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now(), integration_id))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def save_integration_data_mappings(self, integration_id, mappings):
        """Save data mappings for an integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing mappings
            cursor.execute('''
                DELETE FROM integration_data_mappings WHERE integration_id = ?
            ''', (integration_id,))
            
            # Insert new mappings
            for mapping in mappings:
                cursor.execute('''
                    INSERT INTO integration_data_mappings 
                    (integration_id, source_field, target_field, transformation_rule, 
                     is_required, default_value, validation_rule)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    integration_id,
                    mapping.get('source_field'),
                    mapping.get('target_field'),
                    mapping.get('transformation_rule'),
                    mapping.get('is_required', False),
                    mapping.get('default_value'),
                    mapping.get('validation_rule')
                ))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error saving integration data mappings: {e}")
            raise
        finally:
            conn.close()
    
    def get_integration_data_mappings(self, integration_id):
        """Get data mappings for an integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, source_field, target_field, transformation_rule, 
                   is_required, default_value, validation_rule
            FROM integration_data_mappings
            WHERE integration_id = ?
            ORDER BY source_field
        ''', (integration_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'source_field': row[1],
                'target_field': row[2],
                'transformation_rule': row[3],
                'is_required': row[4],
                'default_value': row[5],
                'validation_rule': row[6]
            }
            for row in results
        ]
    
    def save_integration_execution_history(self, integration_id, execution_status, 
                                         records_processed=0, records_success=0, records_failed=0,
                                         execution_time=0.0, error_log=None, output_file_path=None,
                                         triggered_by=None, session_id=None):
        """Save integration execution history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO integration_execution_history
            (integration_id, execution_status, records_processed, records_success,
             records_failed, execution_time_seconds, error_log, output_file_path,
             triggered_by, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            integration_id, execution_status, records_processed, records_success,
            records_failed, execution_time, 
            json.dumps(error_log) if error_log else None,
            output_file_path, triggered_by, session_id
        ))
        
        execution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return execution_id
    
    def get_integration_execution_history(self, integration_id, limit=50):
        """Get execution history for an integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, execution_timestamp, execution_status, records_processed,
                   records_success, records_failed, execution_time_seconds,
                   error_log, output_file_path, triggered_by, session_id
            FROM integration_execution_history
            WHERE integration_id = ?
            ORDER BY execution_timestamp DESC
            LIMIT ?
        ''', (integration_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'execution_timestamp': row[1],
                'execution_status': row[2],
                'records_processed': row[3],
                'records_success': row[4],
                'records_failed': row[5],
                'execution_time_seconds': row[6],
                'error_log': json.loads(row[7]) if row[7] else None,
                'output_file_path': row[8],
                'triggered_by': row[9],
                'session_id': row[10]
            }
            for row in results
        ]
    
    def save_integration_output_config(self, integration_id, output_name, output_format,
                                     output_template=None, output_fields=None,
                                     file_naming_pattern=None, schedule_config=None):
        """Save output configuration for an integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO integration_output_configs
            (integration_id, output_name, output_format, output_template,
             output_fields, file_naming_pattern, schedule_config)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            integration_id, output_name, output_format, output_template,
            json.dumps(output_fields) if output_fields else None,
            file_naming_pattern,
            json.dumps(schedule_config) if schedule_config else None
        ))
        
        config_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return config_id
    
    def get_integration_output_configs(self, integration_id):
        """Get output configurations for an integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, output_name, output_format, output_template,
                   output_fields, file_naming_pattern, schedule_config, is_active
            FROM integration_output_configs
            WHERE integration_id = ? AND is_active = 1
            ORDER BY output_name
        ''', (integration_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'output_name': row[1],
                'output_format': row[2],
                'output_template': row[3],
                'output_fields': json.loads(row[4]) if row[4] else None,
                'file_naming_pattern': row[5],
                'schedule_config': json.loads(row[6]) if row[6] else None,
                'is_active': row[7]
            }
            for row in results
        ]
    
    def update_integration_last_used(self, integration_id):
        """Update the last used timestamp for an integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE external_integrations 
            SET last_used_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (integration_id,))
        
        conn.commit()
        conn.close()

    # LTL Tracking methods
    
    def save_tracking_request(self, upload_history_id, pro_number, carrier_name=None, load_id=None):
        """Save a tracking request for a PRO number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO tracking_requests 
                (upload_history_id, pro_number, carrier_name, load_id)
                VALUES (?, ?, ?, ?)
            ''', (upload_history_id, pro_number, carrier_name, load_id))
            
            tracking_request_id = cursor.lastrowid
            conn.commit()
            
            logging.info(f"Tracking request saved for PRO number: {pro_number}")
            return tracking_request_id
            
        except Exception as e:
            logging.error(f"Error saving tracking request: {e}")
            return None
        finally:
            conn.close()
    
    def save_tracking_result(self, tracking_request_id, tracking_status=None, tracking_location=None, 
                           tracking_event=None, tracking_timestamp=None, scraped_data=None, 
                           scrape_success=True, error_message=None):
        """Save tracking result data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO tracking_results 
                (tracking_request_id, tracking_status, tracking_location, tracking_event, 
                 tracking_timestamp, scraped_data, scrape_success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tracking_request_id, tracking_status, tracking_location, tracking_event, 
                  tracking_timestamp, scraped_data, scrape_success, error_message))
            
            result_id = cursor.lastrowid
            
            # Update tracking request status
            cursor.execute('''
                UPDATE tracking_requests 
                SET status = ? 
                WHERE id = ?
            ''', ('completed' if scrape_success else 'failed', tracking_request_id))
            
            conn.commit()
            
            logging.info(f"Tracking result saved for request ID: {tracking_request_id}")
            return result_id
            
        except Exception as e:
            logging.error(f"Error saving tracking result: {e}")
            return None
        finally:
            conn.close()
    
    def get_tracking_results_for_upload(self, upload_history_id):
        """Get all tracking results for a specific upload"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tr.pro_number, tr.carrier_name, tr.load_id, tr.status,
                   trs.tracking_status, trs.tracking_location, trs.tracking_event,
                   trs.tracking_timestamp, trs.scrape_success, trs.error_message
            FROM tracking_requests tr
            LEFT JOIN tracking_results trs ON tr.id = trs.tracking_request_id
            WHERE tr.upload_history_id = ?
            ORDER BY tr.pro_number
        ''', (upload_history_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'pro_number': row[0],
                'carrier_name': row[1],
                'load_id': row[2],
                'status': row[3],
                'tracking_status': row[4],
                'tracking_location': row[5],
                'tracking_event': row[6],
                'tracking_timestamp': row[7],
                'scrape_success': row[8],
                'error_message': row[9]
            })
        
        conn.close()
        return results
    
    def get_tracking_requests_by_status(self, status='pending'):
        """Get tracking requests by status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, upload_history_id, pro_number, carrier_name, load_id, request_timestamp
            FROM tracking_requests
            WHERE status = ?
            ORDER BY request_timestamp
        ''', (status,))
        
        requests = []
        for row in cursor.fetchall():
            requests.append({
                'id': row[0],
                'upload_history_id': row[1],
                'pro_number': row[2],
                'carrier_name': row[3],
                'load_id': row[4],
                'request_timestamp': row[5]
            })
        
        conn.close()
        return requests