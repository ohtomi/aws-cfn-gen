# -*- coding: utf-8 -*-


class Template(object):

    def __init__(self, version='2010-09-09', description=''):
        self.version = version
        self.description = description
        self.elements = {}

    def __getattr(self, name):
        pass

    def get_section(self, section_name):
        if not self.elements.has_key(section_name):
            self.elements[section_name] = []
        return self.elements[section_name]

    def add_parameter(self, element):
        section = self.get_section('Parameters')
        section.append(element)
        return self

    def add_mappings(self, element):
        section = self.get_section('Mappings')
        section.append(element)
        return self

    def add_resources(self, element):
        section = self.get_section('Resources')
        section.append(element)
        return self

    def add_outputs(self, element):
        section = self.get_section('Outputs')
        section.append(element)
        return self

    def to_template(self):
        template = {}
        template['AWSTemplateFormatVersion'] = self.version
        template['Description'] = self.description
        for section_name, entries in self.elements.items():
            section = template[section_name] = {}
            for element in entries:
                element.to_template(section)

        return template


class Element(object):

    def __init__(self, name):
        self.name = name
        self.attrs = []

    def add_attribute(self, attr):
        self.attrs.append(attr)
        return self

    def to_template(self, template):
        element = template[self.name] = {}
        for attr in self.attrs:
            attr.to_template(element)


class Attribute(object):

    def __init__(self, name, to_template):
        self.name = name
        self.to_template = to_template

    def to_template(self, template):
        self.to_template(template)

    @staticmethod
    def scalar(name, value):
        def to_template(template):
            template[name] = value
        return Attribute(name, to_template)

    @staticmethod
    def dict(name, value):
        def to_template(template):
            template[name] = value
        return Attribute(name, to_template)

    @staticmethod
    def reference(name, element):
        def to_template(template):
            template[name] = {'Ref': element.name}
        return Attribute(name, to_template)


if __name__ == '__main__':
    t = Template(description='Sample Template')
    t.add_parameter(
        Element('KeyName')
            .add_attribute(Attribute.scalar('Description', 'Name of an existing EC2 KeyPair to enable SSH access to the server'))
            .add_attribute(Attribute.scalar('Type', 'String'))
    )
    t.add_parameter(
        Element('InstanceType')
            .add_attribute(Attribute.scalar('Description', 'EC2 instance type'))
            .add_attribute(Attribute.scalar('Type', 'String'))
            .add_attribute(Attribute.scalar('Default', 't1.micro'))
    )
    t.add_mappings(
        Element('RegionToAMI')
            .add_attribute(Attribute.dict('ap-northeast-1', {'AMI': 'ami-a1bec3a0'}))
    )
    vpc = Element('VPC')
    vpc.add_attribute(Attribute.scalar('Type', 'AWS::EC2::VPC'))
    vpc.add_attribute(Attribute.dict('Properties', {'CidrBlock': '10.104.0.0/16', 'InstanceTenancy': 'default'}))
    t.add_resources(vpc)
    t.add_outputs(
        Element('VpcId')
            .add_attribute(Attribute.scalar('Description', '-'))
            .add_attribute(Attribute.reference('Value', vpc))
    )

    #from pprint import PrettyPrinter
    #PrettyPrinter(indent=2).pprint(t.to_template())

    from json import dumps
    print(dumps(t.to_template(), indent=2, separators=(',', ': ')))
