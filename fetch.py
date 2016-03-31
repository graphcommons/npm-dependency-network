import requests
from graphcommons import GraphCommons, Signal
from lxml.html import fromstring
from networkx import DiGraph

from requests.packages import urllib3
urllib3.disable_warnings()


fetched_packages = set()


def import_package_dependencies(graph, package_name, max_depth=3, depth=0):
    if package_name in fetched_packages:
        return

    if depth > max_depth:
        return

    fetched_packages.add(package_name)

    url = 'https://www.npmjs.com/package/%s' % package_name
    response = requests.get(url, verify=False)
    doc = fromstring(response.content)

    graph.add_node(package_name, {
        'type': 'PACKAGE'
    })

    for h3 in doc.cssselect('h3'):
        content = h3.text_content()

        if content.strip().startswith('Collaborators'):

            for collaborator in h3.getnext().cssselect('a'):

                collaborator_name = collaborator.attrib['title']

                graph.add_node(collaborator_name, {
                    'type': 'CONTRIBUTOR'
                })

                graph.add_edge(collaborator_name, package_name, {
                    'type': 'CONTRIBUTED'
                })

        if content.startswith('Dependencies'):
            for dependency in h3.getnext().cssselect('a'):
                dependency_name = dependency.text_content()

                print '-' * depth * 2, dependency_name

                graph.add_node(dependency_name, {
                    'type': 'PACKAGE'
                })

                graph.add_edge(package_name, dependency_name, {
                    'type': 'DEPENDS'
                })

                import_package_dependencies(
                    graph,
                    dependency_name,
                    depth=depth + 1
                )


def main(access_token, package_name, max_depth):
    graph = DiGraph()
    graphcommons = GraphCommons(access_token)
    import_package_dependencies(graph, package_name, max_depth=max_depth)

    signals = []

    for (node, data) in graph.nodes(data=True):

        if data['type'] == 'PACKAGE':
            reference = "https://www.npmjs.com/package/%s" % node
        else:
            reference = 'https://www.npmjs.com/~%s' % node

        signals.append(Signal(
            action="node_create",
            name=node,
            type=data['type'],
            reference=reference
        ))

    for source, target, data in graph.edges(data=True):

        signals.append(Signal(
            action="edge_create",
            from_name=source,
            from_type=graph.node[source]['type'],
            to_name=target,
            to_type=graph.node[target]['type'],
            name=data['type'],
            weight=1
        ))

    created_graph = graphcommons.new_graph(
        name="Dependency Network of %s" % package_name,
        description="Dependency Network of %s Package" % package_name,
        signals=signals
    )

    print 'Created Graph URL:'
    print 'https://graphcommons.com/graphs/%s' % created_graph.id

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--access_token", dest="access_token",
                      help="API Access to use Graph Commons API. You can get "
                           "this token from your profile page on graphcommons.com")
    parser.add_option("--package_name", dest="package_name",
                      help="NPM package that will be fetched")
    parser.add_option("--depth", dest="depth", type=int,
                      help="Max depth of dependencies")
    options, args = parser.parse_args()
    main(options.access_token, options.package_name, options.depth)
