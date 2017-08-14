import os
plugin_list = os.listdir(os.path.dirname(__file__))

# either use all...
__all__ = [os.path.splitext(p)[0] for p in plugin_list if p.endswith('.py') and not (p.startswith('__') or 'base_plugin' in p)]

# or define yours
#__all__ = ['cpu_live', 'cpu', 'cpu_peak', 'diskspace', 'external_ip', 'machine_info', 'memory', 'ssh_tunnel']