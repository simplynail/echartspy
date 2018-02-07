import core

option_overrides = {
    'tooltip': {
        'trigger': 'axis',
    },
    'xAxis':{
        'type':'category'}
}

series_styling = {
    'itemStyle': {
        'emphasis': {
            'shadowBlur':10,
            'shadowOffsetX':0,
            'shadowColor':'rgba(0,0,0,0.5)'
        }
    }
}

class Bar(core.Chart):
    option = core.Chart._update_dict_recursive(core.option_default,option_overrides)

    def __init__(self,categories,title=None):
        super().__init__(typ='bar',title=title)
        self._categories = categories

    def add_series(self, name, data=None, typ=None, stack=None):
        super().add_series(name,data=data,typ=typ,stack=stack)

        if not typ or typ == 'bar':
            series = self._series[-1]
            series.update(**series_styling)

    def generate_tag_js_chart(self):
        extra_option = {
            'xAxis':{
                'data':self._categories
            }
        }
        self.set_option(extra_option)
        return super().generate_tag_js_chart()


if __name__ == '__main__':
    pie = Bar(['chiller','hdac'])

    data = [42,15]
    pie.add_series('electricity',data=data,stack='money')
    pie.add_series('water', data=[15,30], stack='money')

    pie.save_html()