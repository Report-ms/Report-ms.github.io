import os
import importlib
import time
import sys
import requests
import json
import traceback
from datetime import datetime
import debugpy
import threading
import copy  


args = sys.argv[1:]
is_debug = True if len(args) > 4 and args[5] == 'debug' else False
if is_debug:
    print('start debug server...')
    port_for_debug = int(args[6])
    debugpy.listen(("localhost", port_for_debug))  
    print('Debug server started')
    print('Wait for connect client...')
    debugpy.wait_for_client()  
    print('start debugger')
sys.stdout.reconfigure(encoding='utf-8')



def get_translit_string(str):
    if str == "Пользователи":
        return "Users"
    if str == "Пользователь":
        return "User"
    if str == "Имя":
        return "Name"
    if str == "Имя":
        return "Name"
    if str == "Пароль":
        return "Password"
    if str == "Роль":
        return "Role"

    lat_up = ["A", "B", "V", "G", "D", "E", "Yo", "Zh", "Z", "I", "Y", "K", "L", "M", "N", "O", "P", "R", "S", "T", "U", "F", "Kh", "Ts", "Ch", "Sh", "Shch", "\"", "Y", "'", "E", "Yu", "Ya"]
    lat_low = ["a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "\"", "y", "'", "e", "yu", "ya"]
    rus_up = ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ", "Ы", "Ь", "Э", "Ю", "Я"]
    rus_low = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]
    for i in range(33):
        str = str.replace(rus_up[i], lat_up[i])
        str = str.replace(rus_low[i], lat_low[i])
    str = str.replace(" ", "_")
    str = str.replace("'", "_")
    str = str.replace('"', "_")
    return str


def resolve_field(configuration_dictionary, name):
    fields_candidates = list(filter(lambda x: x['ruName'] == name, configuration_dictionary['columns']))
    if len(fields_candidates) == 0:
        dictionary_name = configuration_dictionary['ruNameMany']
        raise Exception(f'Not found field "{name}" in dictionary "{dictionary_name}"')
    return fields_candidates[0]


def resolve_field_name(configuration_dictionary, name):
    return resolve_field(configuration_dictionary, name)['name']


def first_char_to_lower(s):
    if not s:
        return s  
    return s[0].lower() + s[1:]

def to_string(value):
    if type(value) is DictionaryObject:
        return value.id
    if type(value) is datetime:
        return value.strftime("%d.%m.%Y %H:%M:%S")
    if type(value) is list:
        return list(map(to_string, value)) if len(value) > 0 else value
    return value

def Role(app, name):
    rolesCandidates = list(filter(lambda x: x['ruNameSingle'] == name, app.configuration['roles']))
    if len(rolesCandidates) == 0:
        allRolesCount = len(app.configuration['roles'])
        rolesNames = list(map(lambda x: x['ruNameSingle'], app.configuration['roles']))
        raise Exception(f'Not found role "{name}"! Has {allRolesCount} roles: {rolesNames}')
    return rolesCandidates[0]['nameSingle']


def Enum(app, name, value):
    enum_type = list(filter(lambda x: x['ruNameSingle'] == name, app.configuration['enums']))[0]
    return list(filter(lambda x: x['ruNameSingle'] == value, enum_type['values']))[0]['nameSingle']
    
class DictionaryObject:
    def __init__(self, dictionary, id):
        self.dictionary = dictionary
        self.id = id
        self.is_fetched = False
        
    def __str__(self):
        if self.is_fetched is False:
            self.data = self.dictionary.app.requests_session.get(f'{self.dictionary.app.base_url}/{self.dictionary.strictNameMany}/getById/{self.id}', headers=self.dictionary.app.headers).json()
            self.is_fetched = True
        filed_name = self.dictionary.configuration_dictionary['fieldForDefaultNameOfLinkTo']
        return f'{self.dictionary.name}: {self.data[filed_name]} ({self.id})'

    def set(self, name, value = None):
        data = self.dictionary.app.requests_session.get(f'{self.dictionary.app.base_url}/{self.dictionary.strictNameMany}/getById/{self.id}', headers=self.dictionary.app.headers).json()
        if type(name) is str:
            for key in data:
                data[key] = to_string(data[key])
            data[resolve_field_name(self.dictionary.configuration_dictionary, name)] = to_string(value)
        else:
            for key in name:
                data[resolve_field_name(self.dictionary.configuration_dictionary, key)] = to_string(to_string(name[key]))
        response = self.dictionary.app.requests_session.post(f'{self.dictionary.app.base_url}/{self.dictionary.strictNameMany}/createOrUpdate/ru', json=data, headers=self.dictionary.app.headers)
        self.is_fetched = False

    def get(self, name):
        field = '' if name == 'Дата создания' else resolve_field(self.dictionary.configuration_dictionary, name)
        if self.is_fetched is False:
            self.data = self.dictionary.app.requests_session.get(f'{self.dictionary.app.base_url}/{self.dictionary.strictNameMany}/getById/{self.id}', headers=self.dictionary.app.headers).json()
            self.is_fetched = True
        if name == 'Дата создания':
            return datetime.strptime(self.data['CreateAt'], "%Y-%m-%dT%H:%M:%SZ")
        field_value = self.data[field['name']] if field['name'] in self.data else None
        if field['type'] == 'linkToDictionary' and type(field_value) is not DictionaryObject and field_value is not None:
            link_to_dictionary_strict_name = field['linkTo']
            link_to_dictionary_ru_name = list(filter(lambda x: x['strictNameMany'] == link_to_dictionary_strict_name, self.dictionary.app.configuration['dictionaries']))[0]['ruNameMany']
            self.data[field['name']] = DictionaryObject(Dictionary(self.dictionary.app, link_to_dictionary_ru_name), field_value)
            field_value = self.data[field['name']]
        if (field['type'] == 'dateTime' or field['type'] == 'date') and field_value is not None and field_value != '':
            field_value = datetime.strptime(field_value, "%d.%m.%Y %H:%M:%S")
        return field_value

    def action(self, action_name, parameters = None):
        actions = self.dictionary.app.requests_session.get(f'{self.dictionary.app.base_url}/{self.dictionary.strictNameMany}/getActionsForId/{self.id}', headers=self.dictionary.app.headers).json()['actions']
        #action_SetPasswordManually;SetPasswordManually;Установить пароль
        def get_ru_name(action):
            strict_action_name = action['name']
            action_index = f'action_{strict_action_name};'
            return list(filter(lambda x: action_index in x, self.dictionary.app.configuration['translates']))[0].split(';')[2]
        action = list(filter(lambda x: get_ru_name(x) == action_name, actions))[0]
        strict_action_name = action['name']
        print(str(action))
        data = {}

        def get_by_ru_name(fields, field_name):
            return list(filter(lambda x: x['ruName'] == field_name, fields))[0]['name']

        if parameters is not None:
            fields = action['parametersInfo']['fields']
            for parameter in parameters:
                data[get_by_ru_name(fields, parameter)] = parameters[parameter]
        result = self.dictionary.app.requests_session.post(f'{self.dictionary.app.base_url}/{self.dictionary.strictNameMany}/invokeAction/{strict_action_name}/ForId/{self.id}', json=data, headers=self.dictionary.app.headers).json()
        print(str(result))
        return result
        
    def delete(self):
        self.dictionary.app.requests_session.delete(f'{self.dictionary.app.base_url}/{self.dictionary.strictNameMany}/delete/{self.id}/ru', headers=self.dictionary.app.headers)


class Dictionary:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        self.configuration_dictionary = list(filter(lambda x: x['ruNameMany'] == self.name, self.app.configuration['dictionaries']))[0]
        self.strictNameMany = self.configuration_dictionary['strictNameMany']

    def __str__(self):
        return f'Dictionary: {self.name}'

    def get_by_id(self, id):
        return DictionaryObject(self, id)

    def count(self):
        return self.app.requests_session.get(f'{self.app.base_url}/{self.strictNameMany}/getList/0/1', headers=self.app.headers).json()['totalCount']

    def find(self, dict_search):
        search = ''
        index = 0
        for key in dict_search:
            val = dict_search[key]
            if type(dict_search[key]) is DictionaryObject:
                val = dict_search[key].id
            else:
                if type(val) is dict and (val['from'] is not None or val['to'] is not None):
                    val = f'{val['from'].strftime("%d.%m.%Y")}<->{val['to'].strftime("%d.%m.%Y")}'
                else:
                    val = f'-equal-{val}'
            search += ('' if index == 0 else '&') + f'{resolve_field_name(self.configuration_dictionary, key)}={val}'
            index += 1
        url = f'{self.app.base_url}/{self.strictNameMany}/getList/0/100?{search}'
        print(url)
        result = self.app.requests_session.get(url, headers=self.app.headers).json()['rows']
        return list(map(lambda x: DictionaryObject(self, x['Id']), result))

    def all(self):
        return self.find({})

    def create(self, dict_obj):
        data = {}
        for key in dict_obj:
            data[resolve_field_name(self.configuration_dictionary, key)] = to_string(dict_obj[key])
        response = self.app.requests_session.post(f'{self.app.base_url}/{self.strictNameMany}/createOrUpdate/ru', headers=self.app.headers, json=data).json()
        errorMessage = response['errorMessage']
        if errorMessage != None and errorMessage != '':
            raise Exception(f'Error on create "{self.strictNameMany}": {errorMessage}')
        return DictionaryObject(self, response['id'])

class ControllerContextParameters():
    def __init__(self, app, init_string):
        self.app = app
        self.init_string = init_string

    def get(self, name):
        value = json.loads(self.init_string)[name]
        return value


class ContextParameters():
    def __init__(self, app, init_string, action_name):
        self.app = app
        self.init_string = init_string
        self.action_name = action_name
        action_candidates = list(filter(lambda x: x['name'] == action_name, app.configuration['actions']))
        if len(action_candidates) == 0:
            print(app.configuration['actions'])
            raise Exception(f'Action "{action_name}" not found')
        self.action = action_candidates[0]

    def get(self, name):
        field = list(filter(lambda x: x['ruName'] == name, self.action['parametersInfo']['fields']))[0]
        value = json.loads(self.init_string)[field['name']]
        if field['type'] == 'file':
            file_id = json.loads(value)['id']
            file_name = json.loads(value)['name']
            get_token_url = f'{self.app.base_url}/file/createDownloadToken?fileId={file_id}&name={file_name}'
            token = self.app.requests_session.get(get_token_url, headers=self.app.headers).json()['token']
            return f'{self.app.base_url}/file/downloadBy?token={token}'
            # df = pd.read_excel()
            
            # Вывод первых 5 строк DataFrame  
            #print(df.head())

        if field['type'] == 'linkToDictionary' and type(value) is not DictionaryObject and value is not None:
            link_to_dictionary_strict_name = field['linkTo']
            link_to_dictionary_ru_name = list(filter(lambda x: x['strictNameMany'] == link_to_dictionary_strict_name, self.app.configuration['dictionaries']))[0]['ruNameMany']
            value = DictionaryObject(Dictionary(self.app, link_to_dictionary_ru_name), value)
        if (field['type'] == 'dateTime' or field['type'] == 'date') and value is not None and value != '':
            value = datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
        return value        

class DictionaryObjectForMigrator:
    def __init__(self, migrator, dictionary, json_object):
        self.migrator = migrator
        self.dictionary = dictionary
        self.json_object = json_object
        self.id = json_object["Id"]
    def get(self, field_name):
        return self.json_object[get_translit_string(field_name)]
        
    def set(self, field_name, value):
        self.json_object[get_translit_string(field_name)] = value
        file_path = os.path.join(self.migrator.data_folder, get_translit_string(self.dictionary.name) + ".json")
        objects = json.load(open(file_path, encoding='utf-8'))
        objects = list(map(lambda x: self.json_object if x['Id'] == self.id else x, objects))
        json.dump(objects, open(file_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

class DictionaryForMigrator:
    def __init__(self, migrator, name):
        self.migrator = migrator
        self.name = name
    def find(self, filters):
        file_path = os.path.join(self.migrator.data_folder, get_translit_string(self.name) + ".json")
        objects = json.load(open(file_path, encoding='utf-8'))
        result = []
        for json_object in objects:
            is_valid = False
            dictionary_object = DictionaryObjectForMigrator(self.migrator, self, json_object)
            filters_keys_count = len(list(filters.keys()))
            if filters_keys_count == 0:
                is_valid = True
            else:
                passed_filters_count = 0
                for key in filters:
                    val = filters[key]
                    validation_function = lambda x: x == val
                    if type(filters[key]) is DictionaryForMigrator:
                        validation_function = lambda x: x == filters[key].id
                    else:
                        if type(val) is dict and (val['from'] is not None or val['to'] is not None):
                            validation_function = lambda x: val['from'] >= x and val['to'] <= x
                    if validation_function(dictionary_object.get(key)):
                        passed_filters_count += 1
                if passed_filters_count == filters_keys_count:
                    is_valid = True
            if is_valid:
                result.append(dictionary_object)
        return result
    def all(self):
        self.find({})

class Migrator:
    def __init__(self, data_folder):
        self.data_folder = data_folder
    def dictionary(self, name):
        return DictionaryForMigrator(self, name)
    def role(self, name):
        return get_translit_string(name)
    
class App:
    def __init__(self, url):
        self.base_url = f'{url}/api'
        self.requests_session = requests.Session()
        self.output_files = []
        self.instanseId = None
        
    def set_token(self, token):
        self.headers = {"Authorization": f"Bearer {token}"}
        self.update_configuration()
    
    def set_data_folder(self, folder):
        self.data_folder = folder


    def set_password(self, user, password):
        response = self.requests_session.post(f'{self.base_url}/system/setPassword?userId={user.id}&password={password}', headers=self.headers)

    def update_configuration(self):
        response = self.requests_session.get(f'{self.base_url}/configuration' + (f'?instanseId={self.instanseId}' if self.instanseId is not None else ''), headers=self.headers)
        self.configuration = response.json()
        if self.configuration['commonLibrary'] is not None and self.configuration['commonLibrary'] != '':
            spec = importlib.util.spec_from_file_location("commonModule.name", self.configuration['commonLibrary'])  
            module = importlib.util.module_from_spec(spec)  
            spec.loader.exec_module(module)  
            app.common = module

    def temp(self):
        return self.data_folder + "/temp/"
    def send_email(self, to, title, body, files=[]):
        def try_get_id(x):
            if type(x) is str:
                if ':' in x:
                    return json.loads(x)['id']
                return x
            else:
                return x.id
        response = self.requests_session.post(f'{self.base_url}/system/sendEmail', headers=self.headers, json={
            'to': to, 
            'title': title, 
            'body': body,
            'files': list(map(try_get_id, files))
        })
        
    def upload_image(self, path):
        response = self.requests_session.post(f'{self.base_url}/file/uploadImage', headers=self.headers, files={'file': open(path, 'rb')})
        return json.dumps(response.json())

    def upload_file(self, path):
        response = self.requests_session.post(f'{self.base_url}/file/upload', headers=self.headers, files={'file': open(path, 'rb')})
        return json.dumps(response.json())
        
    def set_token_by_login_password(self, login, password):
        identity = self.requests_session.get(f'{self.base_url}/identity/getToken?login={login}&password={password}', headers=self.headers).json()
        self.set_token(identity['data']['accessToken'])
        
    def dictionary(self, name):
        return Dictionary(self, name)
        
    def role(self, name):
        return Role(self, name)
        
    def enum(self, name, value):
        return Enum(self, name, value)
        
    def users(self):
        return Dictionary('Пользователи')

    def notify(self, user, text):
        return self.requests_session.post(f'{self.base_url}/notifications/sendForUser?userId={user.id}&message={text}', headers=self.headers)

    def mail(self, mail, title, body):
        return self.requests_session.post(f'{self.base_url}/system/sendMail', headers=self.headers, json={'mail': mail, 'title': title, 'body': body })

    def chat(self, user_from, user_to, text):
        return self.requests_session.post(f'{self.base_url}/system/sendChat', headers=self.headers, json={'from': user_from.id, 'to': user_to.id, 'text': text })

    def sql(self, sql):
        return self.requests_session.post(f'{self.base_url}/system/executeSql', headers=self.headers, json={'sql': sql }).json()

    def get_parameter(self, name):
        system_parameters = self.requests_session.get(f'{self.base_url}/system/parameters', headers=self.headers).json()
        metadata = system_parameters['metadata']
        metadata_field = list(filter(lambda x: x['ruName'] == name, metadata))[0]
        return system_parameters['values'][first_char_to_lower(metadata_field['name'])]

    def set_parameter(self, name, value):
        system_parameters = self.requests_session.get(f'{self.base_url}/system/parameters', headers=self.headers).json()
        metadata = system_parameters['metadata']
        metadata_field = list(filter(lambda x: x['ruName'] == name, metadata))[0]
        system_parameters['values'][first_char_to_lower(metadata_field['name'])] = value
        return self.requests_session.post(f'{self.base_url}/system/parameters/save', headers=self.headers, json=system_parameters['values']).json()

    def set_context(self, context_dictionary_name, context_object_id, context_user_id, context_parameters, context_action_name):
        if context_dictionary_name != '' and context_object_id != '':
            self.context_object = self.dictionary(context_dictionary_name).get_by_id(context_object_id)

        if context_user_id != '':
            self.context_user = self.dictionary('Пользователи').get_by_id(context_user_id)

        if context_parameters != '' and context_parameters != '{}' and context_action_name != '' and not context_action_name.endswith('Event'):
            if context_action_name.endswith('Controller'):
                self.context_parameters = ControllerContextParameters(self, context_parameters)
            else:
                self.context_parameters = ContextParameters(self, context_parameters, context_action_name)
        else:
            self.context_parameters = None
    def add_result_file(self, file):
        self.output_files.append(file)


def load_and_run_script(tasks_directory, context_file_name, script_path, app):
    result = ''
    is_error = False
    script_path = script_path.replace('\\', '/')
    try:
        # Импортируем модуль по имени  
        spec = importlib.util.spec_from_file_location("module.name", script_path)  
        module = importlib.util.module_from_spec(spec)  
        spec.loader.exec_module(module)  

        # Проверяем, что есть метод run и вызываем его  
        if hasattr(module, 'run'):
            app.output_files = []
            result = module.run(app)
        else:
            result = f"Method 'run' not found in module \"{script_path}\"."
    except ModuleNotFoundError:
        result = f"Module \"{script_path}\" not found."
        is_error = True
    except Exception as e:
        result = f"Error in module \"{script_path}\": {traceback.format_exc()}"
        is_error = True
    #result = json.dumps(result, ensure_ascii = False)
    new_file_name = context_file_name.replace('.json', '_result.json')
    with open(os.path.join(tasks_directory, new_file_name), 'w', encoding='utf-8') as f:
        json.dump({
            'isError': is_error,
            'message': result,
            'files': app.output_files,
            'openNewPages': []
        }, f, ensure_ascii=False, indent=4)


def monitor_directory(appFolder, dataFolder, tasks_directory, app):
    
    known_contexts = set()
    start_time = time.time()
    pid = os.getpid()
    with open(os.path.join(appFolder, dataFolder, 'python_worker_pid'), "w") as f:
        f.write(str(pid))
    counter = 0
    while True:
        current_contexts = {f: os.path.getmtime(os.path.join(tasks_directory, f))
                           for f in os.listdir(tasks_directory) if f.endswith('.json')}
        
        new_contexts = {name: mtime for name, mtime in current_contexts.items()
                       if mtime > start_time and name not in known_contexts}

        for context in new_contexts:
            if context.endswith('_result.json'):
                continue
            context_object = json.load(open(os.path.join(tasks_directory, context), encoding='utf-8'))
            if 'isMigration' in context_object and context_object["isMigration"] == True:
                threading.Thread(target=load_and_run_script, args=(tasks_directory, context, os.path.join(appFolder, context_object['scriptPath']), Migrator(dataFolder))).start()
                pass
            else:
                app.set_context(context_object['dictionary'], context_object['contextObjectId'], context_object['contextUserId'], json.dumps(context_object['params'], ensure_ascii = False), context_object['action'])
                app_copied = copy.copy(app)  
                threading.Thread(target=load_and_run_script, args=(tasks_directory, context, os.path.join(appFolder, context_object['scriptPath']), app_copied)).start()
            known_contexts.add(context) 

        time.sleep(0.1)
        counter = counter + 1
        if counter % 100 == 0:
            app.update_configuration()
            counter = 0
        if is_debug and not debugpy.is_client_connected():
            print('Worker debug stopped!')
            app.requests_session.get(f'{app.base_url}/stopDebug')
            break

appUrl = args[0]
appFolder = args[1]
dataFolder = args[2]
token = args[3]
app = App(appUrl)
app.set_data_folder(dataFolder)
app.set_token(token)
app.instanseId = args[4]

time.sleep(3)

monitor_directory(appFolder, dataFolder, appFolder + '/' + dataFolder + '/tasks', app)  