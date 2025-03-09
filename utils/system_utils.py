import psutil
import datetime
import platform

def get_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

def get_system_info():
    """Get detailed system information"""
    try:
        info = {}
        # CPU information
        info['cpu_percent'] = psutil.cpu_percent(interval=1)
        info['cpu_cores'] = psutil.cpu_count()
        info['cpu_freq'] = psutil.cpu_freq().current
        
        # Memory information
        memory = psutil.virtual_memory()
        info['total_memory'] = get_size(memory.total)
        info['available_memory'] = get_size(memory.available)
        info['memory_percent'] = memory.percent
        
        # Disk information
        disk = psutil.disk_usage('/')
        info['total_disk'] = get_size(disk.total)
        info['free_disk'] = get_size(disk.free)
        info['disk_percent'] = disk.percent
        
        # Battery information if available
        battery = psutil.sensors_battery()
        if battery:
            info['battery_percent'] = battery.percent
            info['power_plugged'] = battery.power_plugged
            
        # Network information
        network = psutil.net_io_counters()
        info['bytes_sent'] = get_size(network.bytes_sent)
        info['bytes_received'] = get_size(network.bytes_recv)
        
        return info
    except Exception as e:
        return f"Error getting system info: {str(e)}"
