#!/bin/bash

##############################################################################
# Tax-Ease EC2 Deployment Script
# This script deploys the Tax-Ease backend services on an EC2 instance
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/taxease"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/taxease"
ADMIN_API_PORT=8001
CLIENT_API_PORT=8002

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo ""
    echo "=========================================================================="
    echo -e "${BLUE}$1${NC}"
    echo "=========================================================================="
    echo ""
}

##############################################################################
# STEP 1: System Requirements Check
##############################################################################
check_system_requirements() {
    print_header "STEP 1: Checking System Requirements"
    
    local all_good=true
    
    # Check Python version
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
        print_success "Python $PYTHON_VERSION installed"
        
        # Check if Python >= 3.9
        MIN_VERSION="3.9"
        if [[ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]]; then
            print_error "Python version must be >= 3.9"
            all_good=false
        fi
    else
        print_error "Python 3 is not installed"
        all_good=false
    fi
    
    # Check pip
    print_status "Checking pip..."
    if command -v pip3 &> /dev/null; then
        print_success "pip3 is installed"
    else
        print_error "pip3 is not installed"
        all_good=false
    fi
    
    # Check PostgreSQL client
    print_status "Checking PostgreSQL client..."
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL client installed"
    else
        print_warning "PostgreSQL client not found (optional for database checks)"
    fi
    
    # Check Redis
    print_status "Checking Redis..."
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            print_success "Redis is running"
        else
            print_warning "Redis is installed but not running"
        fi
    else
        print_warning "Redis not found (will be needed for production)"
    fi
    
    # Check available ports
    print_status "Checking if ports are available..."
    if lsof -Pi :$ADMIN_API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $ADMIN_API_PORT is already in use"
    else
        print_success "Port $ADMIN_API_PORT is available"
    fi
    
    if lsof -Pi :$CLIENT_API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $CLIENT_API_PORT is already in use"
    else
        print_success "Port $CLIENT_API_PORT is available"
    fi
    
    # Check disk space
    print_status "Checking disk space..."
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -gt 5 ]; then
        print_success "Sufficient disk space: ${AVAILABLE_SPACE}GB available"
    else
        print_error "Low disk space: Only ${AVAILABLE_SPACE}GB available"
        all_good=false
    fi
    
    # Check memory
    print_status "Checking memory..."
    TOTAL_MEM=$(free -g | awk 'NR==2 {print $2}')
    if [ "$TOTAL_MEM" -gt 1 ]; then
        print_success "Sufficient memory: ${TOTAL_MEM}GB RAM"
    else
        print_warning "Low memory: Only ${TOTAL_MEM}GB RAM"
    fi
    
    if [ "$all_good" = false ]; then
        print_error "System requirements check failed. Please install missing components."
        exit 1
    fi
    
    print_success "All system requirements satisfied!"
}

##############################################################################
# STEP 2: Install System Dependencies
##############################################################################
install_system_dependencies() {
    print_header "STEP 2: Installing System Dependencies"
    
    if [ "$EUID" -ne 0 ]; then
        print_warning "Not running as root. Will attempt with sudo..."
        SUDO="sudo"
    else
        SUDO=""
    fi
    
    print_status "Updating package lists..."
    $SUDO apt-get update -qq
    
    print_status "Installing system packages..."
    $SUDO apt-get install -y -qq \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libpq-dev \
        postgresql-client \
        redis-server \
        nginx \
        supervisor \
        git \
        curl \
        lsof \
        net-tools
    
    print_success "System dependencies installed"
}

##############################################################################
# STEP 3: Setup Project Directory
##############################################################################
setup_project_directory() {
    print_header "STEP 3: Setting Up Project Directory"
    
    if [ ! -d "$PROJECT_DIR" ]; then
        print_status "Creating project directory: $PROJECT_DIR"
        sudo mkdir -p "$PROJECT_DIR"
        sudo chown $USER:$USER "$PROJECT_DIR"
    fi
    
    # Copy project files if running from current directory
    if [ "$(pwd)" != "$PROJECT_DIR" ]; then
        print_status "Copying project files to $PROJECT_DIR..."
        sudo rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
            --exclude='node_modules' --exclude='.git' \
            ./ "$PROJECT_DIR/"
        sudo chown -R $USER:$USER "$PROJECT_DIR"
    fi
    
    # Create log directory
    if [ ! -d "$LOG_DIR" ]; then
        print_status "Creating log directory: $LOG_DIR"
        sudo mkdir -p "$LOG_DIR"
        sudo chown $USER:$USER "$LOG_DIR"
    fi
    
    cd "$PROJECT_DIR"
    print_success "Project directory set up at $PROJECT_DIR"
}

##############################################################################
# STEP 4: Create Virtual Environment
##############################################################################
setup_virtual_environment() {
    print_header "STEP 4: Setting Up Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists. Removing..."
        rm -rf "$VENV_DIR"
    fi
    
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    print_status "Upgrading pip..."
    pip install --upgrade pip setuptools wheel -q
    
    print_success "Virtual environment created and activated"
}

##############################################################################
# STEP 5: Install Python Dependencies
##############################################################################
install_python_dependencies() {
    print_header "STEP 5: Installing Python Dependencies"
    
    source "$VENV_DIR/bin/activate"
    
    # Install backend dependencies
    if [ -f "backend/requirements.txt" ]; then
        print_status "Installing backend dependencies..."
        pip install -r backend/requirements.txt
        print_success "Backend dependencies installed"
    fi
    
    # Install admin-api dependencies
    if [ -f "services/admin-api/requirements.txt" ]; then
        print_status "Installing admin-api dependencies..."
        pip install -r services/admin-api/requirements.txt
        print_success "Admin API dependencies installed"
    fi
    
    # Install additional common packages
    print_status "Installing additional packages..."
    pip install gunicorn python-multipart aiofiles
    
    print_success "All Python dependencies installed"
}

##############################################################################
# STEP 6: Configure Environment
##############################################################################
configure_environment() {
    print_header "STEP 6: Configuring Environment"
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        print_status "Please create .env file with database and configuration settings"
        exit 1
    fi
    
    print_status "Loading environment variables from .env..."
    source .env
    
    # Validate critical environment variables
    local missing_vars=()
    
    [ -z "$DB_HOST" ] && missing_vars+=("DB_HOST")
    [ -z "$DB_NAME" ] && missing_vars+=("DB_NAME")
    [ -z "$DB_USER" ] && missing_vars+=("DB_USER")
    [ -z "$DB_PASSWORD" ] && missing_vars+=("DB_PASSWORD")
    [ -z "$JWT_SECRET" ] && missing_vars+=("JWT_SECRET")
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    print_success "Environment configuration validated"
    
    # Test database connection
    print_status "Testing database connection..."
    if PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &> /dev/null; then
        print_success "Database connection successful"
    else
        print_error "Cannot connect to database at $DB_HOST"
        print_warning "Services will start but may fail without database access"
    fi
}

##############################################################################
# STEP 7: Setup Systemd Services
##############################################################################
setup_systemd_services() {
    print_header "STEP 7: Setting Up Systemd Services"
    
    print_status "Creating systemd service files..."
    
    # Admin API Service
    sudo tee /etc/systemd/system/taxease-admin-api.service > /dev/null <<EOF
[Unit]
Description=Tax-Ease Admin API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/services/admin-api
Environment="PATH=$VENV_DIR/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 0.0.0.0 --port $ADMIN_API_PORT --workers 2
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/admin-api.log
StandardError=append:$LOG_DIR/admin-api-error.log

[Install]
WantedBy=multi-user.target
EOF
    
    # Client Backend Service
    sudo tee /etc/systemd/system/taxease-client-api.service > /dev/null <<EOF
[Unit]
Description=Tax-Ease Client API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$VENV_DIR/bin/python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port $CLIENT_API_PORT --workers 2
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/client-api.log
StandardError=append:$LOG_DIR/client-api-error.log

[Install]
WantedBy=multi-user.target
EOF
    
    print_status "Reloading systemd daemon..."
    sudo systemctl daemon-reload
    
    print_success "Systemd services created"
}

##############################################################################
# STEP 8: Start Services
##############################################################################
start_services() {
    print_header "STEP 8: Starting Services"
    
    # Start Redis if not running
    if ! systemctl is-active --quiet redis-server; then
        print_status "Starting Redis..."
        sudo systemctl start redis-server
        sudo systemctl enable redis-server
    fi
    
    # Stop services if already running
    print_status "Stopping existing services if any..."
    sudo systemctl stop taxease-admin-api 2>/dev/null || true
    sudo systemctl stop taxease-client-api 2>/dev/null || true
    
    sleep 2
    
    # Start Admin API
    print_status "Starting Admin API service..."
    sudo systemctl start taxease-admin-api
    sudo systemctl enable taxease-admin-api
    
    sleep 3
    
    # Start Client API
    print_status "Starting Client API service..."
    sudo systemctl start taxease-client-api
    sudo systemctl enable taxease-client-api
    
    sleep 3
    
    print_success "All services started"
}

##############################################################################
# STEP 9: Health Checks
##############################################################################
perform_health_checks() {
    print_header "STEP 9: Performing Health Checks"
    
    # Check service status
    print_status "Checking Admin API status..."
    if sudo systemctl is-active --quiet taxease-admin-api; then
        print_success "Admin API service is running"
    else
        print_error "Admin API service failed to start"
        sudo systemctl status taxease-admin-api --no-pager
    fi
    
    print_status "Checking Client API status..."
    if sudo systemctl is-active --quiet taxease-client-api; then
        print_success "Client API service is running"
    else
        print_error "Client API service failed to start"
        sudo systemctl status taxease-client-api --no-pager
    fi
    
    # Check HTTP endpoints
    sleep 5
    
    print_status "Testing Admin API endpoint..."
    if curl -s -f http://localhost:$ADMIN_API_PORT/docs &> /dev/null; then
        print_success "Admin API is responding on port $ADMIN_API_PORT"
    else
        print_warning "Admin API not responding yet (may still be starting)"
    fi
    
    print_status "Testing Client API endpoint..."
    if curl -s -f http://localhost:$CLIENT_API_PORT/docs &> /dev/null; then
        print_success "Client API is responding on port $CLIENT_API_PORT"
    else
        print_warning "Client API not responding yet (may still be starting)"
    fi
}

##############################################################################
# STEP 10: Setup Nginx Reverse Proxy
##############################################################################
setup_nginx() {
    print_header "STEP 10: Setting Up Nginx Reverse Proxy"
    
    print_status "Creating Nginx configuration..."
    
    sudo tee /etc/nginx/sites-available/taxease > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    # Admin API
    location /api/v1/admin/ {
        proxy_pass http://localhost:8001/api/v1/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Client API
    location /api/v1/ {
        proxy_pass http://localhost:8002/api/v1/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/taxease /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    if sudo nginx -t; then
        print_status "Restarting Nginx..."
        sudo systemctl restart nginx
        sudo systemctl enable nginx
        print_success "Nginx configured and restarted"
    else
        print_error "Nginx configuration test failed"
    fi
}

##############################################################################
# STEP 11: Display Summary
##############################################################################
display_summary() {
    print_header "DEPLOYMENT COMPLETE!"
    
    echo -e "${GREEN}✅ Tax-Ease Backend Deployed Successfully${NC}"
    echo ""
    echo "Service Status:"
    echo "  • Admin API:     $(systemctl is-active taxease-admin-api)"
    echo "  • Client API:    $(systemctl is-active taxease-client-api)"
    echo "  • Redis:         $(systemctl is-active redis-server)"
    echo "  • Nginx:         $(systemctl is-active nginx)"
    echo ""
    echo "API Endpoints:"
    echo "  • Admin API:     http://$(hostname -I | awk '{print $1}'):$ADMIN_API_PORT"
    echo "  • Client API:    http://$(hostname -I | awk '{print $1}'):$CLIENT_API_PORT"
    echo "  • Nginx Proxy:   http://$(hostname -I | awk '{print $1}')/"
    echo ""
    echo "Documentation:"
    echo "  • Admin Docs:    http://$(hostname -I | awk '{print $1}'):$ADMIN_API_PORT/docs"
    echo "  • Client Docs:   http://$(hostname -I | awk '{print $1}'):$CLIENT_API_PORT/docs"
    echo ""
    echo "Useful Commands:"
    echo "  • View Admin logs:   sudo journalctl -u taxease-admin-api -f"
    echo "  • View Client logs:  sudo journalctl -u taxease-client-api -f"
    echo "  • Restart Admin:     sudo systemctl restart taxease-admin-api"
    echo "  • Restart Client:    sudo systemctl restart taxease-client-api"
    echo "  • Check status:      sudo systemctl status taxease-*"
    echo ""
    echo "Log Files:"
    echo "  • $LOG_DIR/admin-api.log"
    echo "  • $LOG_DIR/client-api.log"
    echo ""
}

##############################################################################
# Main Execution
##############################################################################
main() {
    print_header "Tax-Ease Backend Deployment Starting..."
    
    # Run all steps
    check_system_requirements
    install_system_dependencies
    setup_project_directory
    setup_virtual_environment
    install_python_dependencies
    configure_environment
    setup_systemd_services
    start_services
    perform_health_checks
    setup_nginx
    display_summary
    
    print_success "Deployment script completed!"
}

# Run main function
main
