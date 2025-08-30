#!/bin/bash

# Test script for local deployment
# This script verifies that the local deployment is working correctly

echo "🧪 Testing Local Deployment..."
echo "================================"

# Check if containers are running
if ! docker-compose ps | grep -q "web-dev.*Up"; then
    echo "❌ web-dev container is not running"
    echo "💡 Run: docker-compose --profile dev up -d --build"
    exit 1
fi

if ! docker-compose ps | grep -q "db.*Up"; then
    echo "❌ database container is not running" 
    echo "💡 Run: docker-compose --profile dev up -d --build"
    exit 1
fi

echo "✅ Containers are running"

# Test database connection
echo "🗄️ Testing database connection..."
if docker-compose exec db pg_isready -U packinglist_user -d packinglist_dev >/dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Test web application
echo "🌐 Testing web application..."
if curl -s http://localhost:8000 >/dev/null; then
    echo "✅ Web application is responding"
else
    echo "❌ Web application is not responding"
    echo "💡 Check: docker-compose logs web-dev"
    exit 1
fi

# Test admin panel
echo "👤 Testing admin panel..."
if curl -s http://localhost:8000/admin/ | grep -q "Django administration"; then
    echo "✅ Admin panel is accessible"
else
    echo "❌ Admin panel is not working"
fi

echo ""
echo "🎉 Local deployment test completed!"
echo ""
echo "📋 Next Steps:"
echo "   1. Open http://localhost:8000 in your browser"
echo "   2. Test the modal functionality:"
echo "      - Navigate to any packing list"
echo "      - Click 'Add Price' buttons"
echo "      - Verify modals open properly"
echo "   3. Check browser console for debug messages"
echo ""
echo "🔍 Modal Testing:"
echo "   - Look for: '🟢 JAVASCRIPT LOADED' in console"
echo "   - Click Add Price buttons should show: '🟢 Add Price link clicked - SUCCESS!'"
echo "   - Modal should open with price form"