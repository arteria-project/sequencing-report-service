

#import subprocess
#
#
# p = subprocess.Popen(['nextflow', '-config', './summary-report-development/config/nextflow.config', 'run',
#                      './summary-report-development/main.nf',
#                      '--runfolder', '/home/johda411-local/large_disk/data/180126_HSX122_0568_BHLFWLBBXX_small',
#                      '--fastq_screen_db', '/home/johda411-local/large_disk/data/FastQ_Screen_Genomes/',
#                      '--checkqc_config', '/ etc/checkqc/config.yaml'],
#                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
#
# print(p.pid)
# p.poll()
#
#stdout, stderr = p.communicate()
# print("COMMMMMM")
# print(stdout)

# def find(d, tag):
#    if tag in d:
#        yield d[tag]
#    for k, v in d.items():
#        if isinstance(v, dict):
#            yield from find(v, tag)
#
#
#d1 = {'a': 1}
#print(next(find(d1, 'a')))
#
#d2 = {'a': {'b': 2}}
#print(next(find(d2, 'b')))
#
#d3 = {'a': {'b': {'c': 3}}}
#print(next(find(d3, 'c')))

import configparser
import yaml

defaults = {'runfolder_path': '/foo/bar', 'runfolder_name': 'bar', 'current_year': '2019'}
with open('config/app.config', 'r') as f:
    c = yaml.safe_load(f.read())
# print(c)
conf = configparser.ConfigParser(defaults=defaults, interpolation=configparser.ExtendedInterpolation())
params_as_conf_dict = {'nextflow_config': c['nextflow_config']['parameters']}
conf.read_dict(params_as_conf_dict)

print(conf['nextflow_config']['runfolder'])
print(conf['nextflow_config']['runfolder_name'])
print(conf['nextflow_config']['current_year'])

# print(conf['nextflow_parameters']['output_dir'])
