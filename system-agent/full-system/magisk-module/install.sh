#!/system/bin/sh
# GAURANGA Magisk Module Install Script

MODPATH=${0%/*}

# Set permissions
chmod 755 $MODPATH/system/bin/gauranga-agent

# Create symlink if needed
[ -f /system/bin/gauranga-agent ] || ln -s $MODPATH/system/bin/gauranga-agent /system/bin/gauranga-agent

# Copy Python files
mkdir -p /data/local/gauranga
cp -r $MODPATH/../python/* /data/local/gauranga/ 2>/dev/null

echo "✅ GAURANGA Module installed"
echo "📱 Reboot to activate"