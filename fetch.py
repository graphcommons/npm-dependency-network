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

    fetched_packages.add(package_name)

    url = 'https://www.npmjs.com/package/%s' % package_name
    response = requests.get(url, verify=False)
    doc = fromstring(response.content)

    for h3 in doc.cssselect('h3'):
        content = h3.text_content()

        if not content.startswith('Dependencies'):
            continue

        for dependency in h3.getnext().cssselect('a'):
            dependency_name = dependency.text_content()

            print '-' * depth * 2, dependency_name

            graph.add_edge(package_name, dependency_name, {
                'type': 'depends'
            })

            if depth <= max_depth:

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

    for node in graph.nodes():
        signals.append(Signal(
            action="node_create",
            name=node,
            type="Package"
        ))

    for source, target in graph.edges():
        signals.append(Signal(
            action="edge_create",
            from_name=source,
            from_type="Package",
            to_name=target,
            to_type="Package",
            name="DEPENDS",
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
