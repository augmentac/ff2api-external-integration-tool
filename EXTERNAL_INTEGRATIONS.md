# External Integrations Framework

The external integrations framework allows you to connect with external APIs and data sources to enrich your freight data. This feature enables you to pull information from LTL carriers, tracking systems, pricing APIs, and more to create enhanced output files with additional insights.

## Features

### 🔌 Integration Types

The framework supports multiple types of integrations:

- **LTL Carrier**: Integration with LTL carrier systems for rate quotes and tracking
- **Freight API**: Generic freight and logistics API integration
- **Tracking API**: Shipment tracking and visibility API
- **Pricing API**: Freight pricing and rate calculation API
- **Customs API**: Customs and border documentation API
- **Warehouse API**: Warehouse management system integration
- **EDI Integration**: Electronic Data Interchange for freight documents
- **Custom Integration**: Custom API or data source integration

### 🛠 Configuration Options

Each integration type has specific configuration options:

#### LTL Carrier Configuration
- API Base URL
- Carrier Code (e.g., FEDX, UPS, ABFS)
- Available Services (LTL, TL, EXPEDITED, etc.)
- Rate Limit (requests/minute)

#### Freight API Configuration
- API Base URL
- API Version
- Supported Transport Modes
- Request Timeout

#### Tracking API Configuration
- API Base URL
- Tracking Methods (TRACKING_NUMBER, PRO_NUMBER, etc.)
- Update Frequency (REAL_TIME, HOURLY, DAILY)
- Webhook URL (optional)

#### Pricing API Configuration
- API Base URL
- Pricing Models (SPOT_RATE, CONTRACT_RATE, etc.)
- Currency (USD, CAD, EUR, GBP)
- Include Fuel Surcharge option

### 🔐 Authentication Methods

The framework supports multiple authentication methods:

- **API Key**: Standard API key authentication
- **Bearer Token**: OAuth bearer token authentication
- **Basic Auth**: Username/password authentication
- **OAuth**: Full OAuth flow with client credentials
- **Custom**: Custom authentication configurations

### 📤 Output File Generation

Integrations can generate output files in multiple formats:

- **CSV**: Comma-separated values format
- **JSON**: JavaScript Object Notation format
- **Excel**: Microsoft Excel format (.xlsx)

Output files are automatically generated with:
- Configurable field selection
- Custom file naming patterns
- Timestamp-based naming
- Organized storage in `data/outputs/` directory

## How to Use

### 1. Access External Integrations

1. Navigate to the main application
2. Select your brokerage in the sidebar
3. Click on the **"🔌 External Integrations"** tab

### 2. Create a New Integration

1. Go to the **"➕ Add New Integration"** tab
2. Fill in the basic information:
   - Integration Name (e.g., "UPS Tracking API")
   - Integration Type (select from dropdown)
   - Description (optional)

3. Configure the integration settings:
   - API Base URL
   - Type-specific settings
   - Authentication credentials

4. Click **"✅ Create Integration"**

### 3. Execute an Integration

1. Go to the **"📋 Manage Integrations"** tab
2. Find your integration in the list
3. Click **"▶️ Execute"**
4. View the results and generated output files

### 4. View Integration History

1. Go to the **"📊 Integration History"** tab
2. Select an integration from the dropdown
3. View execution metrics and detailed history

## Database Schema

The framework uses the following database tables:

- `integration_types`: Available integration types
- `external_integrations`: Integration configurations
- `integration_data_mappings`: Data mapping rules
- `integration_execution_history`: Execution history and results
- `integration_output_configs`: Output file configurations

## Security Features

- **Encrypted Credentials**: All authentication credentials are encrypted using Fernet encryption
- **Secure Storage**: Credentials are stored securely in the database
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Connection Testing**: Test connections before execution
- **Error Handling**: Comprehensive error handling and logging

## Sample Use Cases

### 1. LTL Rate Shopping
- Configure multiple LTL carrier integrations
- Execute rate requests for shipments
- Compare rates across carriers
- Generate reports with best rates

### 2. Shipment Tracking
- Set up tracking API integrations
- Pull tracking updates for shipments
- Generate tracking reports
- Monitor delivery performance

### 3. Pricing Analysis
- Connect to pricing APIs
- Pull historical pricing data
- Analyze market trends
- Generate pricing insights

### 4. Warehouse Integration
- Connect to warehouse management systems
- Pull inventory data
- Monitor warehouse operations
- Generate operational reports

## Technical Architecture

### External Integration Client
The `ExternalIntegrationClient` class handles:
- Integration type selection
- Handler initialization
- Execution management
- Error handling and logging

### Integration Handlers
Each integration type has a specific handler:
- `LTLCarrierHandler`
- `FreightAPIHandler`
- `TrackingAPIHandler`
- `PricingAPIHandler`
- `WarehouseAPIHandler`
- `CustomsAPIHandler`
- `EDIIntegrationHandler`
- `CustomIntegrationHandler`

### Output File Generator
The `OutputFileGenerator` class handles:
- Multiple output formats
- Custom field selection
- File naming patterns
- Organized file storage

## Development Notes

### Adding New Integration Types

To add a new integration type:

1. Add the type to the `integration_types` table
2. Create a new handler class inheriting from `BaseIntegrationHandler`
3. Implement the `execute()` and `test_connection()` methods
4. Add the handler to the `ExternalIntegrationClient` mapping
5. Create type-specific UI configuration components

### Extending Functionality

The framework is designed to be extensible:
- Add new authentication methods in `BaseIntegrationHandler`
- Create custom output formats in `OutputFileGenerator`
- Add new data transformation options
- Implement scheduled execution capabilities

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Verify API credentials
   - Check network connectivity
   - Validate API endpoint URLs
   - Review rate limiting settings

2. **Authentication Errors**
   - Ensure credentials are correctly configured
   - Check authentication method selection
   - Verify API key headers and formats

3. **Output File Issues**
   - Check file permissions in `data/outputs/`
   - Verify output configuration settings
   - Review field selection and mapping

### Logging

The framework provides comprehensive logging:
- Integration execution logs
- Error details and stack traces
- Performance metrics
- Connection test results

Logs are available in:
- Application console output
- Database execution history
- Generated error reports

## Future Enhancements

Planned improvements include:
- Scheduled integration execution
- Real-time data streaming
- Advanced data transformation rules
- Integration monitoring dashboard
- Webhook integration support
- Multi-tenant isolation
- Advanced security features 