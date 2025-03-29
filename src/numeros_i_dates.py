from enum import Enum
from dataclasses import dataclass
import re
from types import NoneType

DIES_SETMANA = ['dilluns', 'dimarts', 'dimecres', 'dijous', 'divendres', 'dissabte', 'diumenge']
DIES_SETMANA_ABREVIATURA = ['dl', 'dt', 'dc', 'dj', 'dv', 'ds', 'dg']
MESOS_ANY = ['gener', 'febrer', 'març', 'abril', 'maig', 'juny', 'juliol', 'agost', 'setembre', 'octubre', 'novembre', 'desembre']
MESOS_ANY_ABREVIATURA = ['gen', 'feb', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'oct', 'nov', 'des']

RE_MESOS = '|'.join(MESOS_ANY)
RE_SETMANA = '|'
RE_AC = 'aC|a_de_C|abans_de_Crist'
RE_DC = 'dC|d_de_C|després_de_Crist'


NUMEROS = {}
with open('diccionari/numeros.txt') as f:
    for line in f:
        num, paraula = line.split()
        NUMEROS[paraula] = int(num)


numeros_mes = '|'.join(word for word,num in NUMEROS.items() if 1<=num<=31)
numeros_any = '|'.join(word for word,num in NUMEROS.items() if 0<=num<=99)


re_weekday = '|'.join(DIES_SETMANA + DIES_SETMANA_ABREVIATURA)
re_day = r'[1-3]?[0-9]' + '|' + numeros_mes
re_month = '|'.join(MESOS_ANY + MESOS_ANY_ABREVIATURA)
re_year = r'[0-9]{1,4}' + '|' + numeros_any
re_era = RE_AC + '|' + RE_DC

def field(x, pre=''):
    if pre: 
        pre = f'(?:({pre})_)?'
    return f'(?:{pre}({x})_)?'
def sep(x):
    return f'(?:(?:{x})_)?'

re_long_date = re.compile(
    '_' +'(' +
    field(re_weekday) + sep(',') +
    field(re_day, pre='dia') + sep("de") +
    field(re_month, pre='mes_de|-') + sep("de") +
    field(re_year, pre='any|el|el_any|-') +
    field(re_era)
    + ')'
)

@dataclass
class Date:
    weekday:int
    day:int
    month:int
    year:int
    def __str__(self):
        weekday = DIES_SETMANA[self.weekday-1] if self.weekday else '??'
        day = self.day or '??'
        month = self.month or '??'
        year = self.year or '??'
        return f'[{weekday}:{day:02}/{month:02}/{year}:??.??]'
    def __repr__(self):
        return str(self)


def parse_dates_and_times(words):
    dates = []
    for match in re_long_date.finditer(('_'+'_'.join(words)+'_').lower()
                                        .replace("_d'_", '_de_').replace('_del_', '_de_el_').replace("_l'_", "_el_")):
        if match.group(0).strip('_') in ('', ',', 'de', 'el'):
            continue
        elems:list[str] = [x or None for x in match.groups()]
        weekday, pre_day, day, pre_month, month, pre_year, year, era = elems
        info = [weekday, day, month, year, era]
        valid_info = sum(x is not None for x in info)

        if valid_info == 0 or (
            valid_info == 1 and not (
                weekday or
                day and pre_day=='dia' or
                month and month in MESOS_ANY or
                year and (
                    pre_year in ('any', 'el_any') or
                    pre_year=='el' and year and year.isnumeric() and 1000<int(year)<2200 or
                    year.isnumeric() and 1900<int(year)<2100
                )
            )
        ):
            continue
        if (era and not year or 
            day and not month and year):
            continue
            
        if weekday:
            if weekday in DIES_SETMANA:
                weekday = DIES_SETMANA.index(weekday)
            else:
                weekday = DIES_SETMANA_ABREVIATURA.index(weekday)
            weekday += 1
        if day:
            if day in NUMEROS:
                day = NUMEROS[day]
            else:
                day = int(day)
            if not 1<=day<=31:
                continue
        if month:
            if month in MESOS_ANY:
                month = MESOS_ANY.index(month)
            elif pre_month == '-' or pre_year == '-':
                month = MESOS_ANY_ABREVIATURA.index(month)
            else:
                continue
            month += 1
        if year:
            if year in NUMEROS:
                year = NUMEROS[year]
            else:
                year = int(year)
            if year == 0:
                year = 1
        if era:
            assert year is not None
            if re.match(RE_AC):
                year = -year

        assert all(type(x) in (int, NoneType) for x in (weekday, day, month, year))
        dates.append((str(Date(weekday, day, month, year)), elems[0].strip('_')))
    return dates

if __name__ == '__main__':
    llist = []
    with open('corpus/ancora-train.pos.txt', 'r', encoding='utf-8') as f:
        for line in f:
            token, lemma, pos = line.split()
            if pos == 'W' and '??.??' in lemma:
                llist.append((token, lemma))

    for token, lemma in llist:
        print()
        found = parse_dates_and_times(token.split('_'))
        if not found:
            print('ERROR', token, 'not found')
        else:
            if len(found) > 1:
                print('WARNING!', len(found), 'tokens')
            else:
                lemma, token_ = found[0]
                if (token_ != ('_'+token+'_').lower().replace("_d'_", '_de_').replace('_del_', '_de_el_').replace("_l'_", "_el_").strip('_')):
                    print('WARNING!', 'different token')
                for f in found:
                    print(token, lemma)
                    print(f[1], f[0])
