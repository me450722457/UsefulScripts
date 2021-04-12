from prometheus_client.parser import text_string_to_metric_families
# TODO: write data to xlsx
# import pandas as pd
import os
import jinja2


class Prom:
    metric_dir_name = "metrics"
    md_dir_name = "mdfile"
    metric_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), metric_dir_name)
    md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), md_dir_name)

    def __init__(self, metric_file, target_file):
        self.metric_file = metric_file
        self.target_file = target_file
        self.abs_metric_file = os.path.join(self.metric_path, self.metric_file)
        self.abs_target_file = os.path.join(self.md_path, self.target_file)

    def _read(self):
        with open(self.abs_metric_file, 'r') as f:
            return f.readlines()

    def _convert(self):
        data = []
        for metric in self._read():
            for family in text_string_to_metric_families(metric):
                for sample in family.samples:
                    name, labels = sample[:2]
                    label_list = tuple(label for label in labels.keys())
                    data.append([name, label_list])
        return Prom._uniq(data)

    @staticmethod
    def _uniq(data):
        data = list(set([tuple(t) for t in data]))
        return data

    @staticmethod
    def template(data):
        tmp = """
| metric_name | lable |
| --- | --- |
{%- for metric in data %}
| {{metric[0]}} | {{metric[1] | list}} |
{%- endfor %}
        """
        return jinja2.Template(tmp).render(data=data)

    def write_md(self):
        data_to_write = Prom.template(self._convert())
        with open(self.abs_target_file, 'w') as f:
            f.write(data_to_write)


def main():
    metric_files = os.listdir(Prom.metric_path)
    for metric_file in metric_files:
        target_file = metric_file.split('.')[0] + '.md'
        data = Prom(metric_file, target_file)
        data.write_md()


if __name__ == '__main__':
    main()
