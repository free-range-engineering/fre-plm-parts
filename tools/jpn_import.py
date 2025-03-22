import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from enum import Enum
from code_calc import parse_value
from fractions import Fraction


class ComponentCategory(Enum):
    ANA = "ANA"         # op-amps, comparators, A/D, D/A
    CAP = "CAP"         # capacitors
    CON = "CON"         # connectors
    CPD = "CPD"         # Circuit protection devices
    DIO = "DIO"         # diodes
    IND = "IND"         # inductors, transformers
    ICS = "ICS"         # integrated circuits
    MPU = "MPU"         # SOC, SOM, SBC, etc.
    MCU = "MCU"         # Microcontrolleres, modules, etc.
    OPT = "OPT"         # Optical, couplers, phototransistor, etc.
    OSC = "OSC"         # oscillators, Crystals
    PWR = "PWR"         # relays, etc
    RFM = "RFM"         # RF modules, ICs, and related components
    REG = "REG"         # regulators
    RES = "RES"         # resistors
    SEN = "SEN"         # sensors
    SWI = "SWI"         # switch
    XTR = "XTR"         # transistors, FETs


category_map = {
    "Capacitors/Multilayer Ceramic Capacitors MLCC - SMD/SMT": ComponentCategory.CAP,
    "Resistors/Chip Resistor - Surface Mount": ComponentCategory.RES,
    "Connectors/Pin Headers": ComponentCategory.CON,
    "Interface/CAN Transceivers": ComponentCategory.ICS,
    "Transistors/Thyristors/Bipolar (BJT)": ComponentCategory.XTR,
    "Transistors/Thyristors/MOSFETs": ComponentCategory.XTR,
    "Power Management (PMIC)/Voltage Regulators - Linear, Low Drop Out (LDO) Regulators": ComponentCategory.REG,
    "Crystals, Oscillators, Resonators/Crystals": ComponentCategory.OSC,
    'Filters/EMI/RFI Filters (LC, RC Networks)':ComponentCategory.RFM,
    'Circuit Protection/ESD and Surge Protection (TVS/ESD)':ComponentCategory.CPD,
    'Interface/Analog Switches, Multiplexers':ComponentCategory.ICS,
    'Motor Driver ICs/Stepper Motor Driver':ComponentCategory.ICS
    
}


def res_package(package):
    if "Plugin" in package:
        return "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
    if package == "0402":
        return "Resistor_SMD:C_0402_1005Metric"
    if package == "0603":
        return "Resistor_SMD:C_0603_1608Metric"
    if package == "0805":
        return "Resistor_SMD:C_0805_2012Metric"
    if package == "1206":
        return "Resistor_SMD:C_1206_3216Metric"
    return f"UNKNOWN:{package}"


def cap_package(package):
    if package == "0402":
        return "Capacitor_SMD:C_0402_1005Metric"
    if package == "0603":
        return "Capacitor_SMD:C_0603_1608Metric"
    if package == "0805":
        return "Capacitor_SMD:C_0805_2012Metric"
    if package == "1206":
        return "Capacitor_SMD:C_1206_3216Metric"

    return f"UNKNOWN:{package}"


def format_to_row(data: dict):
    try:

        category = category_map[data["Category"]]
        if category == ComponentCategory.CAP:
            code, multiplier, as_base, base_text = parse_value(
                data["Capacitance"], False, False)
            return ",".join([f"CAP-XXXX-{code}{multiplier}",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            "Device:C_Small",
                             cap_package(data["Package"]),
                             data["Capacitance"],
                             data["Voltage Rating"],
                             data["Temperature Coefficient"],  # "Material"
                             data["Tolerance"],
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])

        if category == ComponentCategory.RES:
            code, multiplier, as_base, base_text = parse_value(
                data["Resistance"], True, False)
            return ",".join([f"RES-XXXX-{code}{multiplier}",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            "Device:R_Small",
                             res_package(data["Package"]),
                             data["Resistance"],
                             data["Voltage-Supply(Max)"],
                             str(float(
                                 Fraction(data["Power(Watts)"].replace("W", "")))),
                             data["Tolerance"],
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])

        if category == ComponentCategory.CON:
            return ",".join(["CON-XXXX-XXXX",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            "UNKNOWN",
                             "UNKNOWN",
                             "UNKNOWN",
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])

        if category == ComponentCategory.ICS:
            return ",".join(["ICS-XXXX-XXXX",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            "UNKNOWN",
                             data["Package"],
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])

        if category == ComponentCategory.XTR:
            return ",".join(["XTR-XXXX-XXXX",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            "UNKNOWN",
                             data["Package"],
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])
        if category == ComponentCategory.REG:
            return ",".join(["REG-XXXX-XXXX",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            data["Output Voltage"],
                            data["Output Current"],
                            "UNKNOWN",
                             data["Package"],
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])
        if category == ComponentCategory.OSC:
            return ",".join(["OSC-XXXX-XXXX",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            data["Frequency"],
                            data["Frequency Stability"],
                            data["Load Capacitance"],
                            "UNKNOWN",
                             data["Package"],
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])
        if category == ComponentCategory.RFM:
            return ",".join(["RFM-XXXX-XXXX",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            "UNKNOWN",
                             data["Package"],
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])
            
        if category == ComponentCategory.CPD:
            return ",".join(["CPD-XXXX-XXXX",
                            data["MPN"],
                            data["Manufacturer"].replace(",", " "),
                            data["Description"].replace(",", " "),
                            "UNKNOWN",
                             data["Package"],
                             data["Datasheet"],
                             data["JPN"],
                             data["JPT"]])
            
            
    except KeyError as e:
        print(data)
        raise e


def fetch_info_responce(driver, jpn):

    results = dict()
    url = f"https://www.lcsc.com/search?q={jpn}"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    static_categories = ["category_id",
                         "manufacturer_id",
                         "package_id"]
    for sc in static_categories:
        category = soup.find('td', id=sc)
        category_text = category.get_text(strip=True)
        value = category.find_next_sibling('td').get_text(strip=True)
        results.update({category_text: value})

    for index in range(0, 10):
        category = soup.find('td', id=f"paramsItem{index}")
        if not category:
            break
        category_text = category.get_text(strip=True)
        value = category.find_next_sibling('td').get_text(strip=True)
        results.update({category_text: value})
    try:

        datasheet_td = soup.find('td', id="datasheet_id")
        datasheet_td_text = datasheet_td.get_text(strip=True)
        datasheet_href = datasheet_td.find_next_sibling(
            'td').find("a").attrs["href"]
        results.update({datasheet_td_text: datasheet_href})
    except:
        results.update({"Datasheet": "N/A"})

    MPN_ts = soup.find(
        'td', string=lambda text: text and "Mfr. Part #" in text)
    value = MPN_ts.find_next_sibling('td').get_text(strip=True)
    results.update({"MPN": value})

    description_td = soup.find(
        'td', string=lambda text: text and "Description" in text)
    value = description_td.find_next_sibling('td').get_text(strip=True)
    results.update({"Description": value})
    return results


def fetch_jpt_url(driver, jpn):
    url = f"https://jlcpcb.com/parts/componentSearch?searchTxt={jpn}"
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    jpt = soup.select_one(
        "span[class*='text-12 text-666666 ml-4']")
    jpt_recomended = jpt.find_previous_sibling("svg")
    jpt = jpt.text.strip()
    if jpt_recomended and jpt == "Extended":
        jpt = "Preferred"

    return {"JPT": jpt, "JPN": jpn}


if __name__ == "__main__":
    print("JPN Import Start")
    parser = argparse.ArgumentParser(
        description='Fetch component data from JLCPCB.')
    parser.add_argument('JPN', type=str, nargs='+',
                        help='The list of JPNs to search for')
    parser.add_argument('--only-basic', action='store_true',
                        help='Fetch only basic information', default=False)
    args = parser.parse_args()
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=chrome_options)

        for jpn in args.JPN:
            result = {**fetch_jpt_url(driver, jpn),
                      **fetch_info_responce(driver, jpn)}
            if args.only_basic and result["JPT"] != "Basic" and result["JPT"] != "Preferred":
                print(
                    f"Skipping: {jpn} only basic allowed, found:{result['JPT']}")
                print(result)
                continue

            row = format_to_row(result)

            category = category_map[result["Category"]]
            with open(f"../database/g-{category.value.lower()}.csv", "a", encoding="utf-8") as file:
                file.write("\n"+row)

            if row:
                print(row)
            else:
                print("Unknown result")
                print(result)

    except Exception as e:
        print(f"An error occurred: {e.with_traceback()}")
    finally:
        # pass
        driver.quit()
