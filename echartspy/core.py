# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 16:21:22 2018

@author: pawel.cwiek

echarts example html code: http://echarts.baidu.com/echarts2/doc/start-en.html
https://ecomfe.github.io/echarts-doc/public/en/tutorial.html#Dataset

echarts 3.0 !! : https://ecomfe.github.io/echarts-doc/public/en/index.html

python format: https://pyformat.info/
"""
import os
import re
import json
from uuid import uuid4
from copy import deepcopy
import webbrowser


_str_js_echarts_lib_cdn = 'https://cdn.bootcss.com/echarts/4.0.2/echarts-en.min.js'
_str_js_jquery_lib_cdn = 'http://code.jquery.com/jquery-3.3.1.slim.min.js'

_str_js_src_boilerplate = '<script src="{cdn}"></script>'
_str_htmldiv_chart_boilerplate = '<div id="{uid}" style="{div_style}"></div>'
_str_js_chart_boilerplate = '''
<script type="text/javascript">
    // Initialize after dom ready
    var echart_{uid} = echarts.init(document.getElementById('{uid}')); 
    
    var option_{uid} = {option};        

    // Load data into the ECharts instance 
    echart_{uid}.setOption(option_{uid}); 
</script>
'''

_str_js_async_pointer = '''
{
    name: '{name}',
    data: data.{name}
},
'''
_str_js_chart_async_data_boilerplate = '''
<script>
// Asynchronous data loading 
$.get({url}).done(function (data) {
    echart_{uid}.setOption({
        series: [
        {series_pointers}
        ]
    });
});
</script>
'''

_str_html_doc_template = '''
<!doctype html>
<head>
  <meta charset="utf-8">
  <title>eChart</title>
  {js_src}  
</head>
<body>
    {div_chart}
    {js_chart}
</body>
</html>
'''

div_style_default = {
    'width': '100%',
    'height': '100%',
    'position': 'relative',
    'min-height': '200px',
    'float': 'left',
    'padding-right': '1px',
    'padding-left': '1px'}

option_default = {
        'tooltip': {
                'show': True},
        'legend': {
            'show': True
        },
        'xAxis': {
                'type': 'value',
                'nameLocation': 'center'},
        'yAxis': {
                'type': 'value',
                'nameLocation': 'center'},
        }

#chart_types = ['bar','scatter','line', pie]

class Chart(object):
    option = option_default
    _div_style = div_style_default
    _cdn = _str_js_echarts_lib_cdn
    
    def __init__(self,typ,title=None):
        super(self.__class__,self)
        self._type = typ
        self.uid = str(uuid4()).replace('-','')
        self._series = []
        self._async_series = []
        self._async_url = None
    
        if title: self.set_option({'title':{'text':title}})

    @classmethod
    def set_cdn(cls,url):
        cls._cdn = url

    def set_div_style(self,**kwargs):
        if self._div_style == self.__class__._div_style:
            self._div_style = deepcopy(self.__class__._div_style)
        self._div_style.update(kwargs)

    @staticmethod
    def _update_dict_recursive(base, option_set):
        for key, item in option_set.items():
            if type(item) == dict:
                base[key] = __class__._update_dict_recursive(base.get(key, {}), item)
            else:
                base[key] = item
        return base

    def set_option(self,option):
        '''
        updates eCharts option (recursively - no loss of unspecified options)
        option: dict(dict()) dictionary with additional options (in layout as in eCharts js option)
        '''
        # TODO: this doesnt account for case if option is changed first in instance and then in class
        if self.option == self.__class__.option:
            self.option = deepcopy(self.__class__.option)
        self.option = self._update_dict_recursive(self.option,option)
        
    def add_series(self,name,data=None,typ=None,**kwargs):
        if data == None:
            self._async_series.append(name)
        serie = {'name':name,
                'type':typ if typ else self._type,
                'data':data if data else []}
        serie.update(**kwargs)
        self._series.append(serie)

    def set_async_url(self,url):
        '''
        set url for async queries of data.
        Server response must contain chart data wrapped in objects named same as their corresponding series
        ie response{sales:[1,3,5],returns:[2,4,6]}
        :param url: str: url for async query
        :return: None
        '''
        self._async_url = url

    @staticmethod
    def _to_json(data,indent=4):
        return json.dumps(data,sort_keys=True,indent=indent)

    def generate_tag_div_chart(self):
        return _str_htmldiv_chart_boilerplate.format(uid=self.uid,div_style=str(self._div_style)[1:-1].replace("'","").replace(",",";"))

    def generate_tag_js_chart(self):
        self.option['series'] = self._series
        option = self._to_json(self.option)
        js_chart = _str_js_chart_boilerplate.format(uid=self.uid,option=option)
        if self._async_series != []:
            if not self._async_url:
                raise AttributeError('async data defined but no url provided for async query. Use "set_asunc_url" method to define it')
            async_series_str = ''
            for name in self._async_series:
                async_series_str = async_series_str + _str_js_async_pointer.format(name=name)
            async_query = _str_js_chart_async_data_boilerplate.format(url=self._async_url,uid=self.uid,series_pointers=async_series_str)
            js_chart = js_chart + '\n' + async_query
        # remove quotation marks from attribute names
        #js_chart = re.sub(r'(?<!: )"(\S*?)"', '\\1', js_chart)
        return js_chart

    def generate_tag_js_src(self):
        js_src = _str_js_src_boilerplate.format(cdn=self._cdn)
        if self._async_series != []:
            js_src = js_src + '/n' + _str_js_src_boilerplate.format(cdn=_str_js_jquery_lib_cdn)
        return js_src

    def generate_tags(self):
        '''
        generates html tags
        :return: tuple: (js_src, js_chart, div_chart)
        '''
        js_src = self.generate_tag_js_src()
        js_chart = self.generate_tag_js_chart()
        div_chart = self.generate_tag_div_chart()
        return js_src,js_chart,div_chart
    
    def save_html(self,filename='echart.html',show=True):
        if self._div_style['height'][-1] == '%':
            # if height is in %
            self.set_div_style(height='600px')

        js_src, js_chart, div_chart = self.generate_tags()
        
        html_content = _str_html_doc_template.format(js_src=js_src,js_chart=js_chart,div_chart=div_chart)
                
        with open(filename, 'w') as f:
            f.write(html_content)

        if show:
            webbrowser.open('file://'+os.path.join(os.getcwd(),filename))


if __name__ == "__main__":
    chart = Chart(typ='line')
    
    chart.add_series('costam',[[1,2],[3,4]])
    chart.add_series('costam2', [[5, 6], [7, 8]])

    new_options = {'test': True,
        'test2':{'test3':{'test4':True}}}
    chart.set_option(new_options)
    #chart.set_div_style(width='50%',height='335px')
    chart.save_html()