import psutil
import GPUtil
import wmi
from datetime import datetime
import time
import threading
from utils.system_utils import get_size

class SystemMonitor:
    def __init__(self, speak_callback):
        self.speak_callback = speak_callback
        self._stop_monitoring = False
        self._monitor_thread = None
        self.alert_cooldown = {}
        self.last_alert_time = 0
        self.alert_interval = 900  # Only show non-critical alerts every 15 minutes
        self.monitoring = False
        self.monitor_thread = None
        self.startup_check_done = False

    def get_gpu_info(self):
        """Get GPU information if available"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_info = []
                for gpu in gpus:
                    info = {
                        'name': gpu.name,
                        'load': f"{gpu.load*100}%",
                        'memory_used': f"{gpu.memoryUsed}MB",
                        'memory_total': f"{gpu.memoryTotal}MB",
                        'temperature': f"{gpu.temperature}°C"
                    }
                    gpu_info.append(info)
                return gpu_info
            return None
        except Exception as e:
            return f"Error getting GPU info: {str(e)}"

    def get_battery_info(self):
        """Get detailed battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'power_plugged': battery.power_plugged,
                    'time_left': str(datetime.timedelta(seconds=battery.secsleft)) if battery.secsleft > 0 else "Unknown"
                }
            return None
        except Exception as e:
            return f"Error getting battery info: {str(e)}"

    def get_network_info(self):
        """Get detailed network information"""
        try:
            info = {}
            interfaces = psutil.net_if_stats()
            active_interfaces = []
            
            for interface, stats in interfaces.items():
                if stats.isup:
                    active_interfaces.append(interface)
                    
            net_io = psutil.net_io_counters()
            info['active_interfaces'] = active_interfaces
            info['bytes_sent'] = get_size(net_io.bytes_sent)
            info['bytes_received'] = get_size(net_io.bytes_recv)
            info['packets_sent'] = net_io.packets_sent
            info['packets_received'] = net_io.packets_recv
            
            return info
        except Exception as e:
            return f"Error getting network info: {str(e)}"

    def get_running_processes(self, limit=10):
        """Get information about running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]

    def analyze_startup_programs(self):
        """Analyze startup programs and their impact"""
        try:
            w = wmi.WMI()
            startup_programs = w.Win32_StartupCommand()
            
            startup_info = []
            for program in startup_programs:
                startup_info.append({
                    'name': program.Name,
                    'command': program.Command,
                    'location': program.Location
                })
            
            return startup_info
        except Exception as e:
            return f"Error analyzing startup programs: {str(e)}"

    def _can_alert(self, alert_type, is_critical=False):
        """Check if we should show an alert"""
        now = time.time()
        
        # Always allow critical alerts
        if is_critical:
            return True
            
        # For startup check
        if not self.startup_check_done:
            self.startup_check_done = True
            return True
            
        # For regular alerts, check cooldown
        if now - self.last_alert_time < self.alert_interval:
            return False
            
        self.last_alert_time = now
        return True

    def _monitor_system(self):
        """Background monitoring thread"""
        while not self._stop_monitoring:
            try:
                memory = psutil.virtual_memory()
                is_critical = memory.percent > 97
                should_alert = self._can_alert('memory', is_critical)
                
                if should_alert:
                    if is_critical:
                        print(f"\n⚠️ CRITICAL: Memory usage at {memory.percent}%!")
                        self.speak_callback(f"Warning! Memory usage is critically high at {memory.percent} percent!")
                    elif not self.startup_check_done:
                        if memory.percent > 80:
                            print(f"\nStartup Check: Memory usage is high ({memory.percent}%)")
                            self.speak_callback(f"Note: System is running with high memory usage")
                    elif memory.percent > 90:
                        print(f"\nSystem Alert: High memory usage ({memory.percent}%)")
                        self.speak_callback(f"Memory usage is high")

                # Check battery only if critical or startup
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged:
                    is_critical = battery.percent < 10
                    should_alert = self._can_alert('battery', is_critical)
                    
                    if should_alert:
                        if is_critical:
                            print(f"\n⚠️ CRITICAL: Battery at {battery.percent}%!")
                            self.speak_callback("Warning! Battery is critically low!")
                        elif not self.startup_check_done and battery.percent < 20:
                            print(f"\nStartup Check: Low battery ({battery.percent}%)")
                            self.speak_callback("Note: Battery is running low")

                # Check disk space only if critical or startup
                disk = psutil.disk_usage('/')
                is_critical = disk.percent > 97
                should_alert = self._can_alert('disk', is_critical)
                
                if should_alert:
                    if is_critical:
                        print(f"\n⚠️ CRITICAL: Disk space almost full! ({disk.free // (2**30)}GB free)")
                        self.speak_callback("Warning! Disk space is critically low!")
                    elif not self.startup_check_done and disk.percent > 97:
                        print(f"\nStartup Check: Low disk space ({disk.free // (2**30)}GB free)")
                        self.speak_callback("Note: Disk space is running low")

            except Exception as e:
                print(f"Error in system monitoring: {str(e)}")

            # Sleep between checks
            time.sleep(60)  # Check every minute

    def monitor_continuously(self, interval=5):
        """Monitor system continuously and alert if thresholds are exceeded"""
        self.monitoring = True
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                alerts = []
                if cpu_percent > 95:
                    alerts.append(f"High CPU usage: {cpu_percent}%")
                if memory.percent > 95:
                    alerts.append(f"High memory usage: {memory.percent}%")
                if disk.percent > 95:
                    alerts.append(f"Low disk space: {get_size(disk.free)} remaining")
                    
                if alerts:
                    print("\nSystem Alerts:")
                    for alert in alerts:
                        print(f"⚠️ {alert}")
                        self.speak_callback(f"Alert: {alert}")
                
                time.sleep(interval)
            except Exception as e:
                print(f"Error in continuous monitoring: {str(e)}")
                break

    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_continuously, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def start_background_monitoring(self):
        """Start background monitoring"""
        if self._monitor_thread is None:
            self._stop_monitoring = False
            self._monitor_thread = threading.Thread(target=self._monitor_system)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            
    def stop_background_monitoring(self):
        """Stop background monitoring"""
        self._stop_monitoring = True
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
            self._monitor_thread = None

    def get_battery_info(self):
        """Get battery status information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'power_plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != -1 else None
                }
        except Exception as e:
            print(f"Error getting battery info: {str(e)}")
        return None

    def get_network_info(self):
        """Get network usage information"""
        try:
            net_io = psutil.net_io_counters()
            net_if = psutil.net_if_stats()
            
            # Convert bytes to MB
            bytes_sent = net_io.bytes_sent / (1024 * 1024)
            bytes_recv = net_io.bytes_recv / (1024 * 1024)
            
            return {
                'bytes_sent': f"{bytes_sent:.2f}MB",
                'bytes_received': f"{bytes_recv:.2f}MB",
                'packets_sent': net_io.packets_sent,
                'packets_received': net_io.packets_recv,
                'active_interfaces': [iface for iface, stats in net_if.items() if stats.isup]
            }
        except Exception as e:
            print(f"Error getting network info: {str(e)}")
            return None

    def get_running_processes(self, limit=10):
        """Get list of running processes sorted by CPU usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 0:  # Only include active processes
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu_percent': pinfo['cpu_percent'],
                            'memory_percent': pinfo['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            # Sort by CPU usage and return top processes
            return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
            
        except Exception as e:
            print(f"Error getting process list: {str(e)}")
            return None

    def get_system_info(self):
        """Get current system information"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': f"{memory.used / (1024 * 1024 * 1024):.1f}GB",
                'memory_total': f"{memory.total / (1024 * 1024 * 1024):.1f}GB",
                'disk_percent': disk.percent,
                'free_disk': f"{disk.free / (1024 * 1024 * 1024):.1f}GB"
            }
        except Exception as e:
            print(f"Error getting system info: {str(e)}")
            return None
