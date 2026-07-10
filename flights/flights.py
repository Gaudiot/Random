import webbrowser
import time
from datetime import datetime

def to_dd_mm_yyyy(timestring):
    parts = timestring.split("-")
    if len(parts) != 3:
        raise ValueError("Input should be in the format 'YYYY-MM-DD'")
    year, month, day = parts
    return f"{day}-{month}-{year}"

def azul_date_format(date):
    # Expects date as 'YYYY-MM-DD', returns 'MM/DD/YYYY'
    parts = date.split('-')
    if len(parts) != 3:
        raise ValueError("Date should be in 'YYYY-MM-DD' format")
    year, month, day = parts
    return f"{month}/{day}/{year}"

def skyscanner_date_format(date):
    # Expects date as 'YYYY-MM-DD', returns 'YYMMDD'
    parts = date.split('-')
    if len(parts) != 3:
        raise ValueError("Date should be in 'YYYY-MM-DD' format")
    year, month, day = parts
    return f"{year[2:]}{month}{day}"

def maxMilhasUrlBuilder(origin, destiny, type, date, return_date):
    if type == "Round trip" and return_date:
        return f"https://www.maxmilhas.com.br/busca-passagens-aereas/RT/{origin}/{destiny}/{date}/{return_date}/1/0/0/EC"
    elif type == "One way":
        return f"https://www.maxmilhas.com.br/busca-passagens-aereas/OW/{origin}/{destiny}/{date}/1/0/0/EC"
    return ""

def _123MilhasUrlBuilder(origin, destiny, type, date, return_date):
    date = to_dd_mm_yyyy(date)
    return_date = to_dd_mm_yyyy(return_date)

    if type == "Round trip" and return_date:
        return f"https://123milhas.com/v2/busca?de={origin}&para={destiny}&adultos=1&criancas=0&bebes=0&ida={date}&volta={return_date}"
    elif type == "One way":
        return f"https://123milhas.com/v2/busca?de={origin}&para={destiny}&adultos=1&criancas=0&bebes=0&ida={date}"
    return ""

def zupperUrlBuilder(origin, destiny, type, date, return_date):
    if type == "Round trip" and return_date:
        return f"https://www.zupper.com.br/resultados?type=roundTrip&adultQty=1&childrenQty=0&infantQty=0&onlyBusinessClass=false&slices=%5B%7B%22originAirport%22:%22{origin}%22,%22destinationAirport%22:%22{destiny}%22,%22departureDate%22:%22{date}%22%7D,%7B%22destinationAirport%22:%22{origin}%22,%22originAirport%22:%22{destiny}%22,%22departureDate%22:%22{return_date}%22%7D%5D&filters=%7B%22stops%22:%5B0%5D,%22departureTime%22:%5B%7B%22minTime%22:%2216:00%22,%22maxTime%22:%2221:00%22%7D,%7B%22minTime%22:%2212:00%22,%22maxTime%22:%2221:00%22%7D%5D%7D"
    elif type == "One way":
        return f"https://www.zupper.com.br/resultados?type=oneWay&adultQty=1&childrenQty=0&infantQty=0&onlyBusinessClass=false&slices=%5B%7B%22departureDate%22:%22{date}%22,%22destinationAirport%22:%22{destiny}%22,%22originAirport%22:%22{origin}%22,%22destinationCity%22:%22Recife%22,%22originCity%22:%22Sao%20Paulo%22%7D%5D&filters=%7B%22stops%22:%5B0%5D,%22departureTime%22:%5B%7B%22minTime%22:%2216:00%22,%22maxTime%22:%2223:00%22%7D%5D%7D"
    return ""

def flipmilhasUrlBuilder(origin, destiny, type, date, return_date):
    if type == "Round trip" and return_date:
        return f"https://flipmilhas.com/passagens?adults=1&babies=0&back_date={return_date}&children=0&class=economica&departure_date={date}&destiny={destiny}&origin={origin}&rooms=1&outward_stops=0&return_stops=0&departure_time=16%2C23.59&arrival_time=12%2C23.59"
    elif type == "One way":
        return f"https://flipmilhas.com/passagens?adults=1&babies=0&back_date=&children=0&class=economica&departure_date={date}&destiny={destiny}&origin={origin}&rooms=1&outward_stops=0&return_stops=0&departure_time=16%2C23.59&arrival_time=12%2C23.59"
    return ""

def bookingUrlBuilder(origin, destiny, type, date, return_date):
    if type == "Round trip" and return_date:
        return f"https://flights.booking.com/flights/{origin}.AIRPORT-{destiny}.AIRPORT/?type=ROUNDTRIP&adults=1&cabinClass=ECONOMY&from={origin}.AIRPORT&to={destiny}.AIRPORT&fromCountry=BR&toCountry=BR&depart={date}&return={return_date}&sort=CHEAPEST&depTimeInt=12-17%2C18-23%7C12-17%2C18-23&arrTimeInt=00-23%7C00-23&stops=0&lang=pt-br"
    elif type == "One way":
        return f"https://flights.booking.com/flights/{origin}.AIRPORT-{destiny}.AIRPORT/?type=ONEWAY&adults=1&cabinClass=ECONOMY&from={origin}.AIRPORT&to={destiny}.AIRPORT&fromCountry=BR&toCountry=BR&depart={date}&sort=CHEAPEST&depTimeInt=12-17%2C18-23&arrTimeInt=00-23&stops=0&lang=pt-br"
    return ""

def azulUrlBuilder(origin, destiny, type, date, return_date):
    date = azul_date_format(date)
    return_date = azul_date_format(return_date)

    if type == "Round trip" and return_date:
        return f"https://www.voeazul.com.br/br/pt/home/selecao-voo?c[0].ds={origin}&c[0].std={date}&c[0].as={destiny}&c[1].ds={destiny}&c[1].std={return_date}&c[1].as={origin}&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc=BRL"
    elif type == "One way":
        return f"https://www.voeazul.com.br/br/pt/home/selecao-voo?c[0].ds={origin}&c[0].std={date}&c[0].as={destiny}&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc=BRL"
    return ""

def skyscannerUrlBuilder(origin, destiny, type, date, return_date):
    date = skyscanner_date_format(date)
    return_date = skyscanner_date_format(return_date)
    
    if type == "Round trip" and return_date:
        return f"https://www.skyscanner.com.br/transporte/passagens-aereas/{origin}/{destiny}/{date}/{return_date}/?adultsv2=1&departure-times=960-1439,720-1439&preferdirects=true"
    elif type == "One way":
        return f"https://www.skyscanner.com.br/transporte/passagens-aereas/{origin}/{destiny}/{date}/?adultsv2=1&cabinclass=economy&ref=home&rtn=0&preferdirects=true&outboundaltsenabled=false&inboundaltsenabled=false&departure-times=960-1439,720-1439"
    return ""

def skiplaggedUrlBuilder(origin, destiny, type, date, return_date):
    if type == "Round trip" and return_date:
        return ""
    elif type == "One way":
        return f"https://skiplagged.com/flights/{origin}/{destiny}/{date}/"
    return ""

def open_flight_tab(url):
    try:
        safari = webbrowser.get("safari")
        safari.open_new_tab(url)
    except webbrowser.Error:
        webbrowser.open_new_tab(url)

URL_BUILDERS = [
    ("MaxMilhas", maxMilhasUrlBuilder),
    ("123Milhas", _123MilhasUrlBuilder),
    ("Zupper", zupperUrlBuilder),
    ("Flipmilhas", flipmilhasUrlBuilder),
    ("Booking", bookingUrlBuilder),
    ("Azul", azulUrlBuilder),
    ("Skyscanner", skyscannerUrlBuilder),
    ("Skiplagged", skiplaggedUrlBuilder),
]

def start(date, return_date):
    """
    date: string YYYY-MM-DD (ida)
    return_date: string YYYY-MM-DD (volta)
    """
    # Round trip: CGH->REC e GRU->REC, todos os builders exceto Skiplagged
    # for origin in ["CGH", "GRU"]:
    for origin in ["REC"]:
        for name, builder in URL_BUILDERS:
            if name == "Skiplagged":
                continue
            url = builder(origin, "CGH", "Round trip", date, return_date)
            if url:
                open_flight_tab(url)
                time.sleep(1)
    input("\nPressione Enter para continuar para a próxima seção (One way CGH/GRU → REC)...\n")

    # One way, na ordem: CGH->REC, GRU->REC, (cada um com todos os builders)
    one_way_routes = [
        # ("CGH", "REC"),
        # ("GRU", "REC"),
        ("REC", "CGH"),
    ]
    for origin, destiny in one_way_routes:
        for name, builder in URL_BUILDERS:
            # Para one way, builders que usam return_date internamente recebem date como fallback
            url = builder(origin, destiny, "One way", date, return_date)
            if url:
                open_flight_tab(url)
                time.sleep(1)
    input("\nPressione Enter para continuar para a próxima seção (One way REC → CGH/GRU)...\n")

    # One way, na ordem: REC->CGH, REC->GRU (cada um com todos os builders)
    one_way_routes = [
        # ("REC", "CGH"),
        # ("REC", "GRU"),
        ("REC", "CGH"),
    ]
    for origin, destiny in one_way_routes:
        for name, builder in URL_BUILDERS:
            # Para one way, builders que usam return_date internamente recebem date como fallback
            url = builder(origin, destiny, "One way", return_date, date)
            if url:
                open_flight_tab(url)
                time.sleep(1)


def ask_date(prompt):
    user_input = input(prompt).strip()
    return user_input
        

departure_date = ask_date("Informe a data de ida (YYYY-MM-DD): ")
return_date = ask_date("Informe a data de volta (YYYY-MM-DD): ")
print(f"Data de ida selecionada: {departure_date}")
print(f"Data de volta selecionada: {return_date}")

start(departure_date, return_date)
