# required for now cf (https://github.com/brython-dev/brython/issues/2247)
from javascript import NULL
#from javascript import UNDEFINED
from browser import window

#TODO: remove when inheritance bug solved...
from browser import html
from browser import DOMNode
from browser import webcomponent

#from browser.template import Template

g = globals()
for x in window.Object.getOwnPropertyNames(window):

	if x in g:
		continue

	if x.startswith("on"):
		continue

	if x in ["print", "opener", "frameElement", "InstallTrigger", "def_value"]:
		continue

	value = getattr(window, x, None)
	g[x] = value


def WebComponent(parentClass = None):

	if parentClass == None:
		parentClass = DOMNode
		#parentClass = HTMLElement
	else:
		parentClass = getattr(html, parentClass, None)
		#pass

	class InternalWebComponent(parentClass):

		def __init__(self):
			pass
			parameters = {k[5:] : v for k, v in self.attrs.items() if k.startswith("data-")}
			content = str2DF(self._TEMPLATE_HTML.format(**parameters))

			self.replaceChildren(*content)
			self.init() #TODO: use attach bidule + better createElement...

		def init(self):
			pass

	return InternalWebComponent
	

def handle_fetch(response):
	if response.status == 404:
		return Promise.new( lambda resolv, error : resolv(None)  )
	return response.text()

def handle_css(tagname):

	def handle(response):
		#css = f'{tagname}, [is="{tagname}"] {{ {response} }}'
		#style = document.createElement('style')
		#style.textContent = css;
		document.head <= html.STYLE(f'{tagname}, [is="{tagname}"] {{ {response} }}')

	return handle

def handle_webcomponent( tagname, path, tagtype ):

	def handle(response):
		(html_data, python_data) = response
		WebComponentClass = None

		if html_data == None:
			html_data = ""

		if python_data == None :
			#if tagtype != None:
			#	tagtypeClass = window[document.createElement(tagtype).constructor.name]
			WebComponentClass = WebComponent()
		else:

			exec(compile(python_data, path +"/index.py", 'exec'), globals())

			for name in list(globals() ):

				if name == "NULL":
					continue

				candidate = globals()[name]

				for base in candidate.__bases__:
					if base.__name__ == "InternalWebComponent":
						WebComponentClass = candidate
						break

			if WebComponentClass == None:
				raise Exception("WebComponent class not found")

		#setattr(WebComponentClass, '_TEMPLATE', html.TEMPLATE(html_req.data) )
		setattr(WebComponentClass, '_TEMPLATE_HTML', html_data )

		if tagtype != None:
			webcomponent.define(tagname, WebComponentClass, {"extends": tagtype.lower()}) #TODO: fix bug...
		else:
			webcomponent.define(tagname, WebComponentClass)

		global counter
		counter -= 1

		if counter == 0:
			event = Event.new("WebComponentsLoaded");
			window.dispatchEvent(event)

	return handle

counter = 0
def defineCustomElements(tagname, path, tagtype = None):

	global counter
	counter += 1

	name = path.replace('.', '_').replace('/', '_');

	fetch(path +"/index.css").then(handle_fetch).then(handle_css(tagname))

	html_promise = fetch(path +"/index.html").then(handle_fetch)
	py_promise   = fetch(path +"/index.py").then(handle_fetch)
	p = Promise.all([html_promise, py_promise])

	p.then(handle_webcomponent(tagname, path, tagtype))
	
#TODO: better...
def createElement(tagname, content='', attrs={}, classes=[], data={}):

	attrs = ' '.join([key + '="' + value.replace('"','\\"') +'"' for (key,value) in attrs.items()])
	data  = ' '.join([ 'data-' + key + '="' + value.replace('"','\\"') +'"' for (key,value) in data.items()])

	class_str = ""
	if len(classes):
		class_str = f"class=\"{' '.join(classes)}\""

	string = f"<{tagname} {class_str} {attrs} {data}></{tagname}>"

	o = str2html(string);

	if not isinstance(content, list):
		content = [content]
	o.replaceChildren(*content)

	return o

#//https://stackoverflow.com/questions/494143/creating-a-new-dom-element-from-an-html-string-using-built-in-dom-methods-or-pro
def str2html(html):
	return str2DF(html).firstElementChild

def str2DF(html):
	html = html.strip();
	template = document.createElement('template');
	template.innerHTML = html;
	return template.content

# FakeData class
class FakeData:

	def __init__(self, FAKE_DATA):
		self.FAKE_DATA = FAKE_DATA
		self.FAKE_DATA_IDX = 0

	def getFake(self):
		i = self.FAKE_DATA_IDX
		self.FAKE_DATA_IDX = (i+1) % len(self.FAKE_DATA)
		return self.FAKE_DATA[i]
