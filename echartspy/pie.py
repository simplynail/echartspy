import core

option_overrides = {
    'tooltip': {
        'trigger': 'item',
        'formatter': "{a} <br/>{b} : {c} ({d}%)"
    }
}

series_styling = {
    'radius': '55%',
    'center': ['50%','60%'],
    'itemStyle': {
        'emphasis': {
            'shadowBlur':10,
            'shadowOffsetX':0,
            'shadowColor':'rgba(0,0,0,0.5)'
        }
    }
}

class Pie(core.Chart):
    option = core.Chart._update_dict_recursive(core.option_default,option_overrides)

    def __init__(self,title=None):
        super().__init__(typ='pie',title=title)

    def add_series(self, name, data=None, typ=None):
        if not typ or typ =='pie':
            parts = []
            for key,value in sorted(data.items()): parts.append({'name':key,'value':value})
            data = parts

        super().add_series(name,data=data,typ=typ)

        if not typ or typ == 'pie':
            series = self._series[-1]
            series.update(**series_styling)


if __name__ == '__main__':
    pie = Pie()

    data = {'chiller':42,'hdac':15}
    pie.add_series('electricity',data=data)

    pie.save_html()