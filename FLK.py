from lxml import etree
from io import StringIO
import sys
import zipfile

XsdHM='ReestrMO.xsd'
XsdLM='RestrMOPers.xsd'
XsdVM='ReestrMOMEDPers.xsd'
XsdOM='ReestrOM.xsd'


def TestFLK(ArchivName):
    Archive=zipfile.ZipFile(ArchivName)
    for files in Archive.namelist():
        XmlData=Archive.read(files)
        if files[0]=='H':
            with open(XsdHM, 'r') as SchemaFile:
                SchemaToCheck = SchemaFile.read()
            XMLSchemaDoc = etree.parse(XsdHM)
        elif files[0]=='L':
            with open(XsdLM, 'r') as SchemaFile:
                SchemaToCheck = SchemaFile.read()
            XMLSchemaDoc = etree.parse(XsdLM)
        elif files[0]=='V':
            with open(XsdVM, 'r') as SchemaFile:
                SchemaToCheck = SchemaFile.read()
            XMLSchemaDoc = etree.parse(XsdVM)
        elif files[0]=='O':
            with open(XsdOM, 'r') as SchemaFile:
                SchemaToCheck = SchemaFile.read()
            XMLSchemaDoc = etree.parse(XsdOM)
        XMLSchema = etree.XMLSchema(XMLSchemaDoc)
        try:
            Doc = etree.fromstring(XmlData)
            print('Файл '+files+' сформирован без ошибок.')
        # check for file IO error
        except IOError:
            print('Ошибка чтения файла '+files)
        # check for XML syntax errors
        except etree.XMLSyntaxError as err:
            print('Ошибка в синтаксисе XML файла '+files)
            with open('error_schema.log', 'a') as error_log_file:
                error_log_file.write(str(err.error_log))
            quit()
        except:
            print('Неизвестная ошибка.')
            quit()
        try:
            XMLSchema.assertValid(Doc)
            print('Проверка файла '+files+' по XSD схеме завершена успешно.')
        except etree.DocumentInvalid as err:
            print('Ошибки валидации '+files+' по XSD схеме.')
            with open('error_schema.log', 'a') as error_log_file:
                error_log_file.write(str(err.error_log))
            quit()
        except:
            print('Неизвестная ошибка.')
            quit()
    Archive.close()

if __name__=='__main__':
    if len (sys.argv) == 1:
        print ("Не указан файл на тестирование!")
    else:
        TestFLK(sys.argv[1])
    
    

