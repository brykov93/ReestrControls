from lxml import objectify
import zipfile
import requests
from bs4 import BeautifulSoup
import sys,os
import math
import re
#from dateutil.relativedelta import relativedelta
import datetime
from os.path import join, abspath

requests.utils.DEFAULT_CA_BUNDLE_PATH = join(abspath('.'), 'cacert.pem')
NSIFolder=os.getcwd()+r'\NSI\''
BaseTFOMSUrl='https://tfomssk.ru/informatizatsiya-v-sfere-oms/informatsionnoe-vzaimodeystvie-pri-raschetakh-za-meditsinskuyu-pomoshch/nsi/'
NSIUrl='https://tfomssk.ru/files/nsi/SpravNSI.zip'
DializUslStr='A18.05.002;A18.05.002.002;A18.05.002.001;A18.05.011;A18.05.004;A18.05.002.003;A18.05.003;A18.05.004.001;A18.05.011.001;A18.05.002.005;A18.05.003.002;A18.05.011.002;A18.30.001;A18.30.001.001;A18.30.001.002;A18.30.001.003'
DializUsl=DializUslStr.split(';')
IsFullOplByKFURStr='TS1904.001;TS1906.003;CS1915.008;CS1915.009;TS1916.003;CS1920.010;TS1927.001;TS1927.003;TS1927.005;TS1927.006;TS1927.010;TS1930.004;HS1931.002;TS1931.012;TS1931.018;HS1932.011;HS1932.012;HS1932.013;HS1932.014;HS1932.015;CS1936.001;CS1936.003.1;CS1936.003.2;CS1936.003.3;CS1936.003.4;CS1936.003.5;CS1936.003.6;CS1936.003.7;CS1936.003.8;CS1936.003.9;CS1936.003.10;HS1936.007;HD1902.005.1;HD1902.005.2;HD1902.005.3;HD1902.005.4;HD1902.005.5'
IsFullOplByKFUR=IsFullOplByKFURStr.split(';')
IsFullOplStr='TS1902.001;TS1902.002;СS1902.003;HS1902.004;HS1902.010;HS1902.011;TS1903.002;XS1905.006;XS1905.007;XS1905.008;XS1905.009;XS1905.010;XS1905.011;СS1915.008;СS1915.009;TS1916.005;XS1919.027;XS1919.028;XS1919.029;XS1919.030;XS1919.031;XS1919.032;XS1919.033;XS1919.034;XS1919.035;XS1919.036;OS1919.038;HS1920.005;HS1920.006;СS1920.010;HS1921.001;HS1921.002;HS1921.003;HS1921.004;HS1921.005;HS1921.006;СS1925.004;TS1927.012;HS1927.014;TS1931.017;HS1934.002;СS1936.001;CS1936.003.1;CS1936.003.2;CS1936.003.3;CS1936.003.4;CS1936.003.5;CS1936.003.6;CS1936.003.7;CS1936.003.8;CS1936.003.9;CS1936.003.10;HS1936.007;TD1902.001;НD1902.003;НD1902.004;CD1902.006;НD1902.007;XD1905.003;XD1905.004;XD1905.005;XD1905.006;XD1905.007;CD1915.002;CD1915.003;CD1918.003;XD1919.018;XD1919.019;XD1919.020;XD1919.021;XD1919.022;XD1919.023;XD1919.024;XD1919.025;XD1919.026;XD1919.027;OD1919.028;OD1919.029;HD1920.002;HD1920.003;CD1920.006;HD1921.002;HD1921.003;HD1921.004;HD1921.005;HD1921.006;HD1925.001;HD1925.003;TD1927.001;HD1934.002;CD1936.001;CD1936.004.1;CD1936.004.2.1;CD1936.004.2.2;CD1936.004.3;CD1936.004.4'
IsFullOpl=IsFullOplStr.split(';')
errors=[]


#file=open(r'C:\Users\brykov-ab\Desktop\HM260087_180402.XML','rb')
#s=file.read()
#file.close()
#HM=objectify.fromstring(s)
#print(HM.ZGLV.VERSION)

def FindActualSprav():
    file=open(r'NSI_Version.txt','rb')
    ActualVersion=file.read().decode("utf-8") 
    file.close()
    #try:
    response = requests.get(BaseTFOMSUrl)
    soup = BeautifulSoup(response.text, 'html.parser')
    artist_name_list = soup.findAll(class_='alert')
    NowVersion=artist_name_list[2].a.getText()
    if str(ActualVersion)!=NowVersion:
        print('Имеется более поздняя версия спрапвочников. Перехожу к скачиванию.')
        f=open((NSIFolder+NowVersion).replace("'",''),"wb")
        ufr = requests.get(NSIUrl)
        f.write(ufr.content)
        f.close()
        file=open(r'NSI_Version.txt','w')
        file.write(NowVersion)
        file.close()
        print('Все справочники актуализированы. Перехожу к парсингу.')
    else:
        print('Все справочники актуальны. Перехожу к парсингу.')
    return (NSIFolder+NowVersion).replace("'",'') 
    #except:
        #print('Попытка соединения с сайтом ТФОМС не удалась. Перехожу к парсингу последнего загруженного НСИ.')
        #return (NSIFolder+ActualVersion).replace("'",'') 

def ParsSprav(SpravFileName):
    Archive=zipfile.ZipFile(SpravFileName)
    SpravDict={}
    for files in Archive.namelist():
        if '.xml' in files:
            XmlData=Archive.read(files)
            SpravClass=objectify.fromstring(XmlData)
            SpravName=files.replace('.xml','')
            SlashPos=SpravName.find('/')+1 
            SpravName=SpravName[SlashPos:]
            SpravDict.update({SpravName:SpravClass})
            #print('Обработка справочника '+SpravName)
    Archive.close()
    return SpravDict

def LastSymbols(sub_string, in_string): 
    s = in_string.upper()
    if s[len(s)-len(sub_string):]==sub_string:
        return True 
    else: 
        return False

def RoundUp(X):
    if X < 0:
        return long(math.trunc(X-0.5))
    else:
        return long(math.trunc(X+0.5))
        
def my_roundto_(a):
    return round(a+0.005,2)

def chech_FIO_POL(Surname, Name, Patronymic):
    mask_sur_m = [u'ОВ', u'ИН', u'ЕВ', u'ЁВ', u'ЫН', u'ИЙ', u'ОЙ', u'ЫЙ']
    mask_sur_w = [u'ВА', u'НА', u'АЯ', u'ЯЯ' ]
    mask_name_m = [u'Б', u'В', u'Г', u'Д', u'Ж', u'З', u'К', u'Л', u'М', u'Н', u'П', u'Р', u'С',u'Т', u'Ф', u'Х']
    mask_name_w = [u'А', u'Я', u'Ь']
    mask_patr_m = [u'ИЧ']
    mask_patr_w = [u'НА']
    flag_m = 0
    flag_w = 0
    for s in mask_sur_m:
        if LastSymbols(s, Surname):
            flag_m=flag_m+2
            break
    for s in mask_sur_w: 
        if LastSymbols(s, Surname):
            flag_w=flag_w+2
            break
    for s in mask_name_m: 
        if LastSymbols(s, Name):
            flag_m=flag_m+1
            break
    for s in mask_name_w: 
        if LastSymbols(s, Name):
            flag_w=flag_w+1
            break
    for s in mask_patr_m: 
        if LastSymbols(s, Patronymic):
            flag_m=flag_m+3
            break
    for s in mask_patr_w: 
        if LastSymbols(s, Patronymic):
            flag_w=flag_w+3
            break
    if (flag_m >= flag_w):
        return 'М'
    else:
        return 'Ж'

def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)

def FindPatient(LMClass,ID_PAC):
    for Pac in LMClass.PERS:
        if Pac.ID_PAC==ID_PAC:
            return Pac
        
def FindRegExpForDoc(DOCTYPE):
    SpravData=Sprav['F011']
    for Doc in SpravData.item:
        if Doc.attrib['ID']==str(DOCTYPE):
            return Doc.attrib['RDOCSER'],Doc.attrib['RDOCNUM']

def FindMOPodr(CODE_MO,LPU_POD):
    SpravData=Sprav['F003']
    for MO in SpravData.item:
        if MO.attrib['MCOD']==str(CODE_MO):
            for PODR in MO.PODR.item2:
                if PODR.attrib['ID_PODR']==str(LPU_POD):
                    return True
    return False

def addError(errorText,IdCase,NHISTORY): 
        errors.append([IdCase,NHISTORY,errorText])

def FindFullSpravName(ShortName):
    return ''.join(s for s in Sprav.keys() if ShortName.lower() in s.lower())


def CheckInV004D(DOLGNOST):
    SpravName=FindFullSpravName('V004_D')
    SpravData=Sprav[SpravName]
    for DOLGN in SpravData.item:
        if DOLGN.attrib['ID']==DOLGNOST:
            return True
    return False
    
def CheckProfilPol(PROFIL,POL):
    SpravData=Sprav['SK001']
    for PROF in SpravData.item:
        if PROF.attrib['PROFMEDHELP']==PROFIL:
            ok=0
            if PROF.attrib['IS_MUZG']=='1' and POL=='1':
                ok=ok+1
            elif PROF.attrib['IS_GENS']=='1' and POL=='2':
                ok=ok+1
            if ok==0:
                return False
            else:
                return True

def CheckMKBPol(MKB,Pol):
    SpravData=Sprav['SK003']
    Sex=''
    for DIAG in SpravData.item:
        if DIAG.attrib['MKB_START']==DIAG.attrib['MKB_END'] and DIAG.attrib['MKB_START']==MKB:
            Sex=DIAG.attrib['SEX']
            break
        else:
            for i in range(9):
                if len(DIAG.attrib['MKB_START'])==3:
                    DiagNow=DIAG.attrib['MKB_START']+'.'+str(i)
                else:
                    DiagNow=DIAG.attrib['MKB_START'][:4]+str(i)
                if DIAG.attrib['MKB_START']==MKB or DiagNow==MKB or DIAG.attrib['MKB_END']==MKB:
                    Sex=DIAG.attrib['SEX']
                    break
    if Sex!='':
        return Sex==Pol
    else:
        return True

def CheckMKBOnDate(MKB,DateExit):
    SpravName=FindFullSpravName('M001')
    SpravData=Sprav[SpravName]
    for KLASS in SpravData.KLASS:
        for KlassItem in KLASS.item:
            if hasattr(KlassItem,'BLOCK'):
                for BLOCKItem in KlassItem:
                    for BLOCK in BLOCKItem.BLOCK:
                        for RUBRItem in BLOCK.item1:
                            for RUBR in RUBRItem.RUBR:
                                if RUBR.item2.attrib['ID']==MKB:
                                    if hasattr(RUBR.item2,'DATE_END'):
                                         DEnd=datetime.datetime.strptime(str(RUBR.item2.attrib['DATE_END']), "%Y-%m-%d").date()
                                         return DEnd<DateExit
                    
def CheckMKB(MKB):
    SpravName=FindFullSpravName('M001')
    SpravData=Sprav[SpravName]
    AllMKB=[]
    for KLASS in SpravData.KLASS:
        for KlassItem in KLASS.item:
            if hasattr(KlassItem,'BLOCK'):
                for BLOCKItem in KlassItem:
                    for BLOCK in BLOCKItem.BLOCK:
                        for RUBRItem in BLOCK.item1:
                            for RUBR in RUBRItem.RUBR:
                                if RUBR.item2.attrib['ID_IERARH']==MKB:
                                    AllMKB.append(RUBR.item2.attrib['ID'])
    return len(AllMKB)>1

def FindInV004D(DOLGNOST):
    SpravName=FindFullSpravName('V004_D')
    SpravData=Sprav[SpravName]
    for DOLGN in SpravData.item:
        if DOLGN.attrib['ID']==str(DOLGNOST):
            return DOLGN.attrib['SPECIALMED']
        
def CheckSpecProfil(PROFIL,DOLGNOST):
    SpravData=Sprav['SK002']
    PRVD=FindInV004D(DOLGNOST)
    for PROF in SpravData.item:
        if PROF.attrib['PROFIL']==str(PROFIL) and PROF.attrib['PRVD']==str(PRVD):
            return True
    return False

def FindKSG(KSG):
    SpravName=FindFullSpravName('V001_M')
    SpravData=Sprav[SpravName]
    for KSGS in SpravData.item:
        if KSGS.attrib['ID']==KSG:
            return KSGS

def FindAnotherSluchByPac(IDCASE_Z,ID_PAC,HMClass):
    for Sluch in HMClass.ZAP:
        sluch_now=Sluch.Z_SL[0]
        if Sluch.PACIENT.ID_PAC==ID_PAC and sluch_now.IDCASE_Z!=IDCASE_Z:
            return Sluch
    return None

def GetVidVMP(VID_HMP,ActualDate):
    SpravData=Sprav['V018']
    for VID in SpravData.item:
        if VID.attrib['IDHVID']==str(VID_HMP):
            DateBeg=datetime.datetime.strptime(str(VID.attrib['DATE_BEG']), "%Y-%m-%d").date()
            try:
                DateEnd=datetime.datetime.strptime(str(VID.attrib['DATE_END']), "%Y-%m-%d").date()
            except:
                DateEnd=datetime.datetime.strptime('9999-12-31', "%Y-%m-%d").date()
            if ActualDate>=DateBeg and ActualDate<=DateEnd:
                return VID
    return None

def GetMetodVMP(METOD_HMP,ActualDate):
    SpravData=Sprav['V019']
    for METOD in SpravData.item:
        if METOD.attrib['IDHM']==str(METOD_HMP):
            DateBeg=datetime.datetime.strptime(str(METOD.attrib['DATE_BEG']), "%Y-%m-%d").date()
            try:
                DateEnd=datetime.datetime.strptime(str(METOD.attrib['DATE_END']), "%Y-%m-%d").date()
            except:
                DateEnd=datetime.datetime.strptime('9999-12-31', "%Y-%m-%d").date()
            if ActualDate>=DateBeg and ActualDate<=DateEnd:
                return METOD
    return None

def GetUslInfo(USL):
    SpravData=Sprav['V001']
    for USLUG in SpravData.item:
        if USLUG.attrib['ID']==str(USL):
            return USLUG
    return None
    

def GetKFPU(LPU_POD,ActualDate,TYPE_LEVEL):
    date_beg=datetime.date(2000,1,1)
    SpravData=Sprav['SK008']
    koef_now=None
    for KOEF in SpravData.item:
        if KOEF.attrib['TYPE_KOEF']=='1' and KOEF.attrib['TYPE_LEVEL']==TYPE_LEVEL:
            LPUS=KOEF.MO_LIST.iterchildren()
            for LPU in LPUS:
                if LPU.attrib['ID_PODR']==str(LPU_POD):
                    date_beg_koef=datetime.datetime.strptime(KOEF.attrib['DATE_BEGIN'], "%Y-%m-%d").date()
                    if (date_beg_koef>date_beg and date_beg_koef<=ActualDate):
                        date_beg=date_beg_koef
                        koef_now=KOEF
    if koef_now==None:
        return 0
    else:
        return float(koef_now.attrib['KOEF'])


def GetKSGPrice(KSG,ActualDate,DET):
    date_beg=datetime.date(2000,1,1)
    SpravData=Sprav['SK005']
    for PRICE in SpravData.item:
        if PRICE.attrib['MES']==str(KSG):
            date_beg_price=datetime.datetime.strptime(PRICE.attrib['DATE_BEGIN'], "%Y-%m-%d").date()
            if (date_beg_price>date_beg and date_beg_price<=ActualDate):
                date_beg=date_beg_price
                price_now=PRICE
    price_det=float(price_now.attrib['SUM_DET'])
    price_vzr=float(price_now.attrib['SUM_VZ'])
    if str(DET)=='0':
        price=price_vzr
    elif str(DET)=='1':
        price=price_det
    return price
            

def TestMEK(ArchivName):
    Archive=zipfile.ZipFile(ArchivName)
    HasOnkSluch=False
    for files in Archive.namelist():
        if files[0]=='H':
            XmlDataHM=Archive.read(files)
        elif files[0]=='V':
            XmlDataVM=Archive.read(files)
        elif files[0]=='L':
            XmlDataLM=Archive.read(files)
        elif files[0]=='O':
            XmlDataOM=Archive.read(files)
            HasOnkSluch=True
    Archive.close()
    HMClass=objectify.fromstring(XmlDataHM)
    VMClass=objectify.fromstring(XmlDataVM)
    LMClass=objectify.fromstring(XmlDataLM)
   
    if HasOnkSluch:
        OMClass=objectify.fromstring(XmlDataOM)
    for Sluch in HMClass.ZAP:
        sluch_now=Sluch.Z_SL[0]
        d_exit=datetime.datetime.strptime(str(sluch_now.DATE_Z_2), "%Y-%m-%d").date()
        d_enter=datetime.datetime.strptime(str(sluch_now.DATE_Z_1), "%Y-%m-%d").date()
        patient_info_now=FindPatient(LMClass,Sluch.PACIENT.ID_PAC)
        born=datetime.datetime.strptime(str(patient_info_now.DR), "%Y-%m-%d").date()
        #======================================================================================================================
        #Проверка заполнения документов по маске
        #======================================================================================================================
        if hasattr(patient_info_now,'DOCTYPE'):
            if len(patient_info_now.DOCTYPE)>0:
                regex_ser,regex_num=FindRegExpForDoc(patient_info_now.DOCTYPE)
                if hasattr(patient_info_now,'DOCSER'):
                   if re.search(regex_ser, str(patient_info_now.DOCSER))==None:
                       addError('Серия документа пациента '+patient_info_now.FAM+' '+patient_info_now.IM+' '+patient_info_now.OT+
                                          ' заполнена некорректно!', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                if hasattr(patient_info_now,'DOCNUM'):
                   if re.search(regex_num, str(patient_info_now.DOCNUM))==None:
                       addError('Номер документа пациента '+patient_info_now.FAM+' '+patient_info_now.IM+' '+patient_info_now.OT+
                                          ' заполнен некорректно!', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================
        #Проверка заполнения подразделения МО
        #======================================================================================================================
        PodrInMO=FindMOPodr(HMClass.REESTR.CODE_MO,sluch_now.SLUCH.LPU_POD)
        if not(PodrInMO):
            addError('Подразделение случая не соответствует коду МО', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================
        #Проверка правильности оформления случая до государствеенной регистрации новорожденного пациента
        #======================================================================================================================
        if Sluch.PACIENT.NOVOR!=0:
            novor_date=datetime.datetime.strptime(str(Sluch.PACIENT.NOVOR)[1:3]+str(Sluch.PACIENT.NOVOR)[3:5]+str(Sluch.PACIENT.NOVOR)[5:7], "%d%m%y").date()
            if novor_date+datetime.timedelta(days=90)>d_exit:
                addError('''Указан признак новорожденного, но на момент выписки пациенту более 90 дней!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
            if d_enter+datetime.timedelta(days=1)<novor_date:
                addError('''Дата рождения новорожденного больше даты обращения!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================
        #Проверка соответствия кода врачебной должности оказываемой медицинской помощи по возрастному критерию
        #======================================================================================================================
        if str(sluch_now.SLUCH.DOLGNOST) in ['3019','3018','3020','4099','4098','3104','3904','3042','4105','3043','3902']:
           sov_letie=yearsago(-18, born)
           if sov_letie<d_exit:
               if str(sluch_now.SLUCH.DOLGNOST) in ['3904','3042','4105','3043','3902']:
                   if hasattr(sluch_now.SLUCH,'DS2_N'):
                       if not(str(patient_info_now.W)=='2' and ('Z32' in str(sluch_now.SLUCH.DS2_N.DS2) or
                                                                 'Z33' in str(sluch_now.SLUCH.DS2_N.DS2) or
                                                                 'Z34' in str(sluch_now.SLUCH.DS2_N.DS2) or
                                                                 'Z35' in str(sluch_now.SLUCH.DS2_N.DS2))):
                           addError('''Возраст пациента не соответствует должности врача оказавшего услугу!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
               else:
                   addError('''Возраст пациента не соответствует должности врача оказавшего услугу!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        elif (str(sluch_now.SLUCH.DOLGNOST)=='') or not(CheckInV004D(str(sluch_now.SLUCH.DOLGNOST))) :
               addError('''Не указана должность лечащего врача!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)                   
        if int(sluch_now.USL_OK) in [1,2] and str(sluch_now.SLUCH.PODR)=='':
                addError('''При оказании МП в условиях круглосуточного или дневного стационара обязательно к заполнению 
                поле "Ведущее отделение"''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================            
        #Проверка условия оказания и вида МП
        #Проверка соответствия условия оказания МП форме оказания МП
        #Проверка на указание нескольких услуг по СМП
        #======================================================================================================================
        if str(sluch_now.USL_OK)=='1':
            if str(sluch_now.VIDPOM)[0]!='3':
                addError('''При USL_OK=1 код VIDPOM должен начинаться с 3!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        elif str(sluch_now.USL_OK)=='2':
            if str(sluch_now.VIDPOM)=='32':
                addError('''При USL_OK=2 код VIDPOM не должен быть 32!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        elif str(sluch_now.USL_OK)=='3':
            if str(sluch_now.VIDPOM)[0]!='1':
                addError('''При USL_OK=3 код VIDPOM должен начинаться с 1!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
            if d_exit-d_enter>datetime.timedelta(days=15):
                pass
                #self.addError('''Длительность лечения в амбулатории больше 15 дней. Возможно карту возьмут для проведения дополнительной проверки.''', sluch_now['IDCASE'], sluch_now['NHISTORY'])
        elif str(sluch_now.USL_OK)=='4':
            if str(sluch_now.VIDPOM)[0]!='2':
                addError('''При USL_OK=4 код VIDPOM должен начинаться с 2!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
            if len(sluch_now.SLUCH.USL)>1:
                addError('''Для случая вызова СМП указано более 1 оплачиваемой услуги!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)  
        else:
            addError('''Не указано условие оказание МП!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================
        #Проверка даты оказания МП в реестре счетов на соответствие отчетному периоду/периоду оплаты   
        #======================================================================================================================
        if int(sluch_now.PR_NOV)<=0:
            if d_exit+datetime.timedelta(days=60)<datetime.datetime.strptime(str(HMClass.REESTR.DSCHET), "%Y-%m-%d").date():
                addError('''Случай предъявлен на оплату позднее 2-х месяцев!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================
        #Проверка соответствия типа реестра по ВМП указанному виду помощи   
        #======================================================================================================================
        if str(HMClass.REESTR.TYPE)=='30' and str(sluch_now.VIDPOM)!='32':
            addError('''Для типа реестра по высокотехнологичной МП (30) VIDPOM должен быть равен 32!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        if str(HMClass.REESTR.TYPE)!='60' and str(sluch_now.SLUCH.ONK_SL)=='1':
            addError('''Случай с признаком ОНКО-заболевания должен быть выставлен в реестре с типом 60!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================
        #Проверка профиля оказания МП с полом пациент
        #======================================================================================================================
        if not(CheckProfilPol(str(sluch_now.SLUCH.PROFIL),str(patient_info_now.W))):
            addError('''Профиль оказания МП '''+str(sluch_now.SLUCH.PROFIL)+''' не совместим с полом пациента '''+str(patient_info_now.W),
                     sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================
        #Проверка правильности заполнения ПДн пациента
        #======================================================================================================================
        if str(patient_info_now.W)=='2':
            s='Ж'
        elif str(patient_info_now.W)=='1':
            s='М' 
        if chech_FIO_POL(str(patient_info_now.FAM), str(patient_info_now.IM), str(patient_info_now.OT))!=s:
            addError('''Возможно пол пациента  не соответствует ФИО''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        if born>d_enter:
            addError('''Дата рождения пациента больше даты начала случая!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        if hasattr(sluch_now.SLUCH,'DS1'):
           if str(sluch_now.SLUCH.DS1)!='':
               if not(CheckMKBPol(str(sluch_now.SLUCH.DS1),str(patient_info_now.W))):
                   addError('''Основной диагноз "'''+str(sluch_now.SLUCH.DS1)+'''" не соответствует полу пациента '''+str(patient_info_now.W),
                            sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
               if len(sluch_now.SLUCH.DS1)<=3:
                   if CheckMKB(str(sluch_now.SLUCH.DS1)):
                       addError('''Код МКБ ('''+sluch_now.SLUCH.DS1+''') основного диагноза указан без детализции до подрубрики!''',
                                sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
               if CheckMKBOnDate(str(sluch_now.SLUCH.DS1),d_exit):
                   addError('''Код МКБ ('''+sluch_now.SLUCH.DS1+''') основного диагноза не действует на момент выписки!''',
                                sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)   
           else:
               addError('''Не указан основной диагноз по случаю!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        #======================================================================================================================
        #Проверка на выявление безрезультативных вызовов СМП 
        #======================================================================================================================
        if str(sluch_now.RSLT) in ['407', '408', '409', '410', '411', '412', '413', '414', '415', '416', '417'] and sluch_now.USL_OK=='4':
            addError('''Безрезультативные вызововы СМП оплачиваются по подушевому нормативу финансирования!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
        count_obr=0
        sum_usl=0
        sum_sluch=float(sluch_now.SLUCH.SUMV_LIST.SUM_M)
        first_usl_in_sluch=1
        for usl in sluch_now.SLUCH.USL:
            try:
                sum_temp=float(usl.SUMV_USL_LIST.SUMV_USL)
            except:
                sum_temp=0
                addError('Нулевая стоимость услуги!', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
            sum_usl=sum_usl+sum_temp
            #======================================================================================================================
            #Проверка совместимости профиля специальности врача 
            #======================================================================================================================
            if not(CheckSpecProfil(usl.PROFIL,usl.DOLGNOST)):
                addError('''Медицинская специальность врача на должности '''+str(usl.DOLGNOST)+
                         ''' несовместима с профилем '''+str(usl.PROFIL), sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
            #======================================================================================================================
            #Проверка соответствия дат оказания услуг датам случая
            #======================================================================================================================
            DATE_IN=datetime.datetime.strptime(str(usl.DATE_IN), "%Y-%m-%d").date()
            DATE_OUT=datetime.datetime.strptime(str(usl.DATE_OUT), "%Y-%m-%d").date()
            if not(DATE_IN>=d_enter and DATE_IN<=d_exit and DATE_OUT>=d_enter and DATE_OUT<=d_exit):
                    addError('''Период оказания оплачиваемой услуги ('''+str(DATE_IN)+'''-'''+str(DATE_OUT)+''') не входит в период случая ('''+
                             str(d_enter)+'''-'''+str(d_exit)+''')''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
            if hasattr(usl,'CODE_MES1'):
                ##Стационарные проверки
                ksg_now=FindKSG(usl.CODE_MES1)
                if hasattr(ksg_now,'DATE_END'):
                    ksg_date_end=datetime.datetime.strptime(ksg_now.attrib['DATE_END'], "%Y-%m-%d").date()
                else:
                    ksg_date_end=datetime.datetime.strptime('9999-12-31', "%Y-%m-%d").date()
                if ksg_date_end<DATE_OUT:
                    addError('На момент выписки пациента КСГ '+usl.CODE_MES1+' уже не действителен. Дата окончания '+
                                    'действия КСГ- '+str(ksg_date_end), sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                #======================================================================================================================
                #Проверка нескольких случаев оказания стационарной помощи с пересечением или совпадением сроков лечения
                #======================================================================================================================
                check_sluch=FindAnotherSluchByPac(sluch_now.IDCASE_Z,Sluch.PACIENT.ID_PAC,HMClass)
                if check_sluch!=None:
                    check_sluch_usl=check_sluch.SLUCH.USL
                    for check_usl in check_sluch_usl:
                        if hasattr(check_usl,'CODE_MES1'):
                            check_sluch_d_enter=datetime.datetime.strptime(str(check_usl.DATE_IN), "%Y-%m-%d").date()
                            check_sluch_d_exit =datetime.datetime.strptime(str(check_usl.DATE_OUT), "%Y-%m-%d").date()
                            if check_sluch_d_enter<DATE_IN and check_sluch_d_exit>DATE_IN:
                                self.addError('''Случай '''+str(check_sluch.IDCASE_Z)+''' пересекается со случаем '''+
                                              str(sluch_now.IDCASE_Z), sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                #======================================================================================================================
                #Проверка правильности применения КСГ по ВМП
                #======================================================================================================================
                if str(usl.CODE_MES1)[0]=='V':
                    if str(sluch_now.VIDPOM)!='32':
                        addError('''При оказании КСГ по высокотехнологичной МП, VIDPOM должен быть равен 32!''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                    if hasattr(sluch_now.SLUCH,'VID_HMP'):
                        if str(sluch_now.SLUCH.VID_HMP) not in (usl.CODE_MES1):
                            addError('''Указаный вид высокотехнологичной МП '''+str(sluch_now.SLUCH.VID_HMP)+
                                     ' возможно не соответствует коду КСГ '+str(usl.CODE_MES1), sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                        VID_HMP=GetVidVMP(sluch_now.SLUCH.VID_HMP,DATE_OUT)
                        if VID_HMP==None:
                            addError('''Указаный вид высокотехнологичной МП '''+str(sluch_now.SLUCH.VID_HMP)+
                                     ' не найден в справочнике, или не актуален на дату оказания МП.', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                    if hasattr(sluch_now.SLUCH,'METOD_HMP'):
                        METOD_HMP=GetMetodVMP(sluch_now.SLUCH.METOD_HMP,DATE_OUT)
                        if METOD_HMP!=None:
                            if METOD_HMP.attrib['HVID']!=str(sluch_now.SLUCH.VID_HMP):
                                addError('''Метод высокотехнологичной МП "'''+str(sluch_now.SLUCH.METOD_HMP)+
                                                      '''" не совместим с видом ВМП "'''+str(sluch_now.SLUCH.VID_HMP)+'''"''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                            if ';'+str(usl.DS)+';' not in ';'+METOD_HMP.attrib['DIAG']+';':
                                addError('''Метод высокотехнологичной МП "'''+str(sluch_now.SLUCH.METOD_HMP)+
                                                      '''" не совместим с диагнозом "'''+str(usl.DS)+'''"''', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                        else:
                            addError('''Указаный метод высокотехнологичной МП '''+str(sluch_now.SLUCH.METOD_HMP)+
                                     ' не найден в справочнике, или не актуален на дату оказания МП.', sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                #======================================================================================================================
                #Проверка правильности применения кода КСГ
                #======================================================================================================================
                ##Группировщик пока пропустим. Не было ошибок в подборе КСГ.
                #======================================================================================================================
                #Проверка стоимости услуг
                #======================================================================================================================
                try:
                    sum_temp=float(usl.SUMV_USL_LIST.SUMV_USL)
                except:
                    sum_temp=0
                if sum_temp>0:
                    if str(usl.CODE_MES1)[0]=='V':
                        kfpu=1;
                        kfsl=1;
                        koef_prerv=1;
                        koef_ultrashort=1;
                    else:
                        if str(usl.CODE_MES1) in IsFullOplByKFUR:
                            kfpu=1
                        else:
                            if str(usl.CODE_MES1)[1]=='D':
                                type_level='6'
                            else:
                                type_level='5'
                            #kfpu=GetKFPU(usl.LPU_POD,DATE_OUT,type_level) проблема с отделениями ВМП
                            kfpu=float(sluch_now.SLUCH.KSG.KOEF_U)
                        koef_prerv=1
                        koef_ultrashort=1
                        koef_oper=1
                        if float(usl.KOL_USL)<=3 or str(sluch_now.RSLT) in ['104','102','105','106','107','108','110','202','204','205','206','207','208']:
                            ok=0
                            if hasattr(sluch_now.SLUCH,'USL_OTHER'):
                                for usl_other in sluch_now.SLUCH.USL_OTHER:
                                    if hasattr(usl_other,'CODE_USL'):
                                        if usl_other.CODE_USL in ['B01.001.009.001','B02.001.002','B01.001.006','A16.20.005','A25.24.001.002']:
                                            ok=ok+1
                                        else:
                                            if str(usl.CODE_MES1)[0] in ['C','O','X','H','R']:
                                                UslInfo=GetUslInfo(usl_other.CODE_USL)
                                                if UslInfo!=None and UslInfo.attrib['TYPE']=='13':
                                                    ok=ok+1
                            if ok>0:
                                koef_oper=0.8
                            else:
                                if float(usl.KOL_USL)<=3:
                                    koef_oper=0.3    
                                else:
                                    koef_oper=0.5
                        if float(usl.KOL_USL)<=3:
                            koef_ultrashort=koef_oper
                        if str(sluch_now.RSLT) in ['104','102','105','106','107','108','110','202','204','205','206','207','208']:
                            koef_ultrashort=1
                            koef_prerv=koef_oper
                        if str(usl.CODE_MES1) in IsFullOpl:
                            koef_prerv=1
                            koef_ultrashort=1
                        kfsl=1
                        koef_ksg=1
                        if hasattr(sluch_now.SLUCH.KSG,'IT_KFSK'):
                            kfsl=float(sluch_now.SLUCH.KSG.IT_KFSK)
                        price=GetKSGPrice(usl.CODE_MES1,DATE_OUT,usl.DET)
                        price_dvig=round(price*kfpu*kfsl*koef_prerv*koef_ultrashort*koef_ksg,2)
                        if (round(price_dvig,2)!=sum_temp 
                            and round(price_dvig+0.01,2)!=sum_temp 
                            and round(price_dvig-0.01,2)!=sum_temp 
                            and round(price_dvig*0.5,2)!=sum_temp 
                            and round(price_dvig*0.5+0.01,2)!=sum_temp 
                            and round(price_dvig*0.5-0.01,2)!=sum_temp):
                            str_kfsl='' if kfsl==1 else '*КфСл('+str(kfsl)+')'
                            str_kf_prerv='' if koef_prerv==1 else '*Кф.прерв('+str(koef_prerv)+')'
                            str_kf_ultrashot='' if koef_ultrashort==1 else '*Кф.сверхкор.('+str(koef_ultrashort)+')'
                            str_kf_ksg='' if koef_ksg==1 else '*Кф.КСГ('+str(koef_ksg)+')'
                            addError('''Ошибка расчета стоимости услуги! Тариф МО-'''+str(sum_temp)+
                                          ''', тариф СМО- '''+str(price_dvig)+'''=цена SK005('''+str(price)+
                                          ''')*КфПу('''+str(kfpu)+''')'''+str_kfsl+str_kf_prerv+str_kf_ultrashot+str_kf_ksg+'='+str(price_dvig),
                                     sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                #======================================================================================================================
                #Проверка на полное дублирование услуг имеющих стоимость по стационарной помощи внутри одного реестра счета
                #Проверка на частичное дублирование услуг по стационарной помощи внутри одного реестра счета
                #======================================================================================================================
                if first_usl_in_sluch==1:
                    check_sluch=FindAnotherSluchByPac(sluch_now.IDCASE_Z,Sluch.PACIENT.ID_PAC,HMClass)
                    if check_sluch!=None:
                        last_idcase=''
                        check_sluch_usl=check_sluch.SLUCH.USL
                        for check_usl in check_sluch_usl:
                            if (check_usl.DATE_IN==usl.DATE_IN 
                                and check_usl.DATE_OUT==usl.DATE_OUT
                                and check_usl.PROFIL==usl.PROFIL 
                                and check_usl.LPU_POD==usl.LPU_POD):
                                if last_idcase!=check_sluch.IDCASE_Z:
                                    if usl.CODE_MES1==check_usl.CODE_MES1:
                                        addError('''Случай '''+check_sluch.IDCASE_Z+''' полностью дублирует случай '''+sluch_now.IDCASE_Z,
                                                 sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                                    else:
                                        addError('''Случай '''+check_sluch.IDCASE_Z+''' частично дублирует случай '''+sluch_now.IDCASE_Z,
                                                 sluch_now.IDCASE_Z, sluch_now.SLUCH.NHISTORY)
                                    last_idcase=check_sluch['IDCASE']
                #Конец стационарных проверок
            if hasattr(usl,'CODE_USL'):
                




    #print()
                            


    


if __name__=='__main__':
    if len (sys.argv) == 1:
        print ("Не указан файл на тестирование!")
    else:
        ActualSpravFileName=FindActualSprav()
        Sprav=ParsSprav(ActualSpravFileName)
        TestMEK(sys.argv[1])
        f = open(os.getcwd()+r'\result.txt', 'w')
        if len(errors)>0:
            for error in errors:
                for s in error:
                    f.write(str(s) +'    ')
                f.write('\n')
        else:
            f.write('Ошибок МЭК не найдено!')
        f.close()
