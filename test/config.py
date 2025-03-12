import os
import sys

if 'win' in sys.platform:  # Windows
    sys.path.append('D:\\Git\\Python-WSN-Simulators')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\test')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\attacks')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\core')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\core\\nodes')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\core\\routing')
    # sys.path.append('D:\\Git\\Python-WSN-Simulators\\utils')
else:  # Linux, Unix, MacOS
    sys.path.append('.')