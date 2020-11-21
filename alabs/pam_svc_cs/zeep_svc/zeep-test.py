from zeep import Client, Settings


settings = Settings(strict=False, xml_huge_tree=True)
zc = Client('https://manager-rpa.argos-labs.com/services/QMSService?wsdl',
            settings=settings)

# QMSServiceHttpBinding, QMSServiceSoap11Binding, QMSServiceSoap12Binding
my_binding = '{http://webservice.qms.vivans.net}QMSServiceSoap11Binding'
zcs = zc.create_service(my_binding, 'https://manager-rpa.argos-labs.com/services/QMSService.QMSServiceHttpSoap11Endpoint')

# Getting Supervisor's Time
r = zcs.getServerTime()
print(r)

# Getting Scenario from Supervisor in case of On-Demand
r = zcs.getCollectionSiteV2("1827", "BCEE7B8932BA")
print(r)
