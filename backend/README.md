# LLM Security Scanner Backend API

Backend server for storing and managing LLM Security Scanner results, similar to Semgrep's dashboard.

## Features

- **REST API** for receiving scan results
- **MySQL Database** for persistent storage
- **API Key Authentication** for secure access
- **Application Management** for organizing scans
- **Scan History** with detailed findings
- **Statistics and Analytics** per application

## Prerequisites

- Node.js 18+ 
- MySQL 8.0+
- npm or yarn

## Installation

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Create MySQL database:**
   ```sql
   CREATE DATABASE llm_scan_db;
   ```

5. **Run database migrations:**
   ```bash
   npm run migrate
   ```

6. **Seed database (optional - creates demo data):**
   ```bash
   npm run seed
   ```

## Configuration

Edit `.env` file with your settings:

```env
PORT=3000
NODE_ENV=development

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=llm_scan_db

JWT_SECRET=your-super-secret-jwt-key
```

## Running the Server

### Development Mode (with auto-reload):
```bash
npm run dev
```

### Production Mode:
```bash
npm start
```

The server will start on `http://localhost:3000` (or your configured PORT).

## API Endpoints

### Health Check
```
GET /health
```

### Store Scan Results
```
POST /api/v1/scans
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "application_id": "your-app-id",
  "findings": [...],
  "scanned_files": [...],
  "rules_loaded": [...],
  "scan_duration_seconds": 1.23,
  "metadata": {...}
}
```

### Get Scan List
```
GET /api/v1/scans?page=1&limit=20
Authorization: Bearer <api_key>
```

### Get Scan Details
```
GET /api/v1/scans/:scanId
Authorization: Bearer <api_key>
```

### Get Application Details
```
GET /api/v1/applications/:applicationId
Authorization: Bearer <api_key>
```

### Create API Key
```
POST /api/v1/api-keys
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "name": "My API Key",
  "expires_in_days": 365
}
```

### List API Keys
```
GET /api/v1/api-keys
Authorization: Bearer <api_key>
```

## Database Schema

The database includes the following tables:

- **applications**: Application metadata
- **api_keys**: API key management
- **scans**: Scan execution records
- **findings**: Individual security findings
- **scanned_files**: Files that were scanned
- **rules_loaded**: Rules used in each scan

See `src/db/schema.sql` for full schema details.

## Integration with Scanner

Update your scanner configuration to use this backend:

```bash
trusys-llm-scan . \
  --upload http://localhost:3000/api/v1/scans \
  --api-key sk_your_api_key_here \
  --application-id your-app-id
```

Or set environment variables:

```bash
export LLM_SCAN_API_KEY=sk_your_api_key_here
export LLM_SCAN_APPLICATION_ID=your-app-id

trusys-llm-scan . --upload http://localhost:3000/api/v1/scans
```

## Security Features

- **API Key Authentication**: All endpoints require valid API keys
- **Rate Limiting**: Prevents abuse (100 requests per 15 minutes)
- **Helmet.js**: Security headers
- **Input Validation**: Joi schema validation
- **SQL Injection Protection**: Parameterized queries

## Development

### Project Structure

```
backend/
├── src/
│   ├── server.js          # Main server file
│   ├── db/
│   │   ├── connection.js  # Database connection
│   │   ├── schema.sql     # Database schema
│   │   ├── migrate.js     # Migration script
│   │   └── seed.js        # Seed script
│   ├── middleware/
│   │   └── auth.js        # Authentication middleware
│   └── routes/
│       ├── scans.js       # Scan endpoints
│       ├── applications.js # Application endpoints
│       └── apiKeys.js     # API key management
├── package.json
├── .env.example
└── README.md
```

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database exists: `CREATE DATABASE llm_scan_db;`

### API Key Not Working
- Verify API key exists in database
- Check API key is active: `is_active = TRUE`
- Verify API key hasn't expired
- Check Authorization header format: `Bearer <api_key>`

### Migration Errors
- Ensure database exists before running migrations
- Check MySQL user has CREATE TABLE permissions
- Review error messages for specific table issues

## Production Deployment

1. **Set NODE_ENV=production**
2. **Use strong JWT_SECRET**
3. **Enable HTTPS**
4. **Set up database backups**
5. **Configure proper rate limits**
6. **Set up monitoring and logging**
7. **Use process manager (PM2, systemd, etc.)**

## License

MIT
