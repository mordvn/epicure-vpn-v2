from services.marzban import Marzban
from services.youkassa import Youkassa
def include_services(dp):
    dp['marzban'] = Marzban()
    dp['youkassa'] = Youkassa()