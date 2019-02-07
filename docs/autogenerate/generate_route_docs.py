

from arteria.web.routes import RouteService
from sequencing_report_service.app import routes


route_service = RouteService(app_svc=None, debug=False)
route_service.set_routes(routes())
print("Auto-generated routes documentation")
print("***********************************")
for item in route_service.get_help("http://localhost:9999")['doc']:
    print('{}'.format(item['route']))
    for method_key in item['methods'].keys():
        print('\tMethod: {}'.format(method_key.upper()))
        print("\t\t{}".format(item['methods'][method_key]))
