# Copyright (c) 2015 Amazon.com, Inc. or its affiliates.  All Rights Reserved
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import boto
from boto.compat import json
from boto.connection import AWSAuthConnection
from boto.regioninfo import RegionInfo
from boto.exception import JSONResponseError
from boto.ec2containerservice import exceptions


class EC2ContainerServiceConnection(AWSAuthConnection):
    """
    Amazon EC2 Container Service (Amazon ECS) is a highly scalable,
    fast, container management service that makes it easy to run,
    stop, and manage Docker containers on a cluster of Amazon EC2
    instances. Amazon ECS lets you launch and stop container-enabled
    applications with simple API calls, allows you to get the state of
    your cluster from a centralized service, and gives you access to
    many familiar Amazon EC2 features like security groups, Amazon EBS
    volumes, and IAM roles.

    You can use Amazon ECS to schedule the placement of containers
    across your cluster based on your resource needs, isolation
    policies, and availability requirements. Amazon EC2 Container
    Service eliminates the need for you to operate your own cluster
    management and configuration management systems or worry about
    scaling your management infrastructure.
    """
    APIVersion = "2014-11-13"
    DefaultRegionName = "us-east-1"
    DefaultRegionEndpoint = "ecs.us-east-1.amazonaws.com"
    ResponseError = JSONResponseError

    _faults = {
        "ServerException": exceptions.ServerException,
        "ClientException": exceptions.ClientException,
    }


    def __init__(self, **kwargs):
        region = kwargs.pop('region', None)
        if not region:
            region = RegionInfo(self, self.DefaultRegionName,
                                self.DefaultRegionEndpoint)

        if 'host' not in kwargs or kwargs['host'] is None:
            kwargs['host'] = region.endpoint

        super(EC2ContainerServiceConnection, self).__init__(**kwargs)
        self.region = region

    def _required_auth_capability(self):
        return ['hmac-v4']

    def create_cluster(self, cluster_name=None):
        """
        Creates a new Amazon ECS cluster. By default, your account
        will receive a `default` cluster when you launch your first
        container instance. However, you can create your own cluster
        with a unique name with the `CreateCluster` action.

        During the preview, each account is limited to two clusters.

        :type cluster_name: string
        :param cluster_name: The name of your cluster. If you do not specify a
            name for your cluster, you will create a cluster named `default`.

        """
        params = {}
        if cluster_name is not None:
            params['clusterName'] = cluster_name
        return self._make_request(
            action='CreateCluster',
            verb='POST',
            path='/', params=params)

    def create_service(self, service_name, cluster=None, desired_count=None,
                       load_balancers=None, role=None, task_definition=None):
        """
        Runs and maintains a desired number of tasks from a specified task
        definition. If the number of tasks running in a service drops below
        `desired_count`, Amazon ECS will spawn another instantiation of the
        task in the specified cluster.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that you want to run your service on. If you do not
            specify a cluster, the default cluster is assumed.

        :type desired_count: integer
        :param desired_count: The number of instantiations of the specified
            task definition that you would like to place and keep running on
            your cluster.

        :type load_balancers: list of tuples
        :param load_balancers: A list of load balancer tuples, containing the
            load balancer name, the container name (as it appears in a
            container definition), and the container port to access from the
            load balancer.

        :type role: string
        :param role: The name or full Amazon Resource Name (ARN) of the IAM
            role that allows your Amazon ECS container agent to make calls to
            your load balancer on your behalf. This parameter is only required
            if you are using a load balancer with your service.

        :type service_name: string
        :param service_name: The name of your service. Up to 255 letters
            (uppercase and lowercase), numbers, hyphens, and underscores are
            allowed.

        :type task_definition: string
        :param task_definition: The `family` and `revision` (`family:revision`)
            or full Amazon Resource Name (ARN) of the task definition that you
            want to run in your service.
        """
        params = {}
        params['serviceName'] = service_name
        if cluster is not None:
            params['cluster'] = cluster
        if desired_count is not None:
            params['desiredCount'] = desired_count
        if load_balancers is not None:
            self.build_complex_list_params(
                params, load_balancers, 'loadBalancer.member',
                ('LoadBalancerName', 'ContainerName', 'ContainerPort'))
        if role is not None:
            params['role'] = role
        if task_definition is not None:
            params['taskDefinition'] = task_definition

        return self._make_request(
            action='CreateService',
            verb='POST',
            path='/', params=params)

    def delete_cluster(self, cluster):
        """
        Deletes the specified cluster. You must deregister all
        container instances from this cluster before you may delete
        it. You can list the container instances in a cluster with
        ListContainerInstances and deregister them with
        DeregisterContainerInstance.

        :type cluster: string
        :param cluster: The cluster you want to delete.

        """
        params = {'cluster': cluster, }
        return self._make_request(
            action='DeleteCluster',
            verb='POST',
            path='/', params=params)

    def deregister_container_instance(self, container_instance, cluster=None,
                                      force=None):
        """
        Deregisters an Amazon ECS container instance from the
        specified cluster. This instance will no longer be available
        to run tasks.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the container instance you want to
            deregister. If you do not specify a cluster, the default cluster is
            assumed.

        :type container_instance: string
        :param container_instance: The container instance UUID or full Amazon
            Resource Name (ARN) of the container instance you want to
            deregister. The ARN contains the `arn:aws:ecs` namespace, followed
            by the region of the container instance, the AWS account ID of the
            container instance owner, the `container-instance` namespace, and
            then the container instance UUID. For example, arn:aws:ecs: region
            : aws_account_id :container-instance/ container_instance_UUID .

        :type force: boolean
        :param force: Force the deregistration of the container instance. You
            can use the `force` parameter if you have several tasks running on
            a container instance and you don't want to run `StopTask` for each
            task before deregistering the container instance.

        """
        params = {'containerInstance': container_instance, }
        if cluster is not None:
            params['cluster'] = cluster
        if force is not None:
            params['force'] = str(
                force).lower()
        return self._make_request(
            action='DeregisterContainerInstance',
            verb='POST',
            path='/', params=params)

    def deregister_task_definition(self, task_definition):
        """
        Deregisters the specified task definition. You will no longer
        be able to run tasks from this definition after
        deregistration.

        :type task_definition: string
        :param task_definition: The `family` and `revision` (
            `family:revision`) or full Amazon Resource Name (ARN) of the task
            definition that you want to deregister.

        """
        params = {'taskDefinition': task_definition, }
        return self._make_request(
            action='DeregisterTaskDefinition',
            verb='POST',
            path='/', params=params)

    def describe_clusters(self, clusters=None):
        """
        Describes one or more of your clusters.

        :type clusters: list
        :param clusters: A space-separated list of cluster names or full
            cluster Amazon Resource Name (ARN) entries. If you do not specify a
            cluster, the default cluster is assumed.

        """
        params = {}
        if clusters is not None:
            self.build_list_params(params,
                                   clusters,
                                   'clusters.member')
        return self._make_request(
            action='DescribeClusters',
            verb='POST',
            path='/', params=params)

    def describe_container_instances(self, container_instances, cluster=None):
        """
        Describes Amazon EC2 Container Service container instances.
        Returns metadata about registered and remaining resources on
        each container instance requested.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the container instances you want to
            describe. If you do not specify a cluster, the default cluster is
            assumed.

        :type container_instances: list
        :param container_instances: A space-separated list of container
            instance UUIDs or full Amazon Resource Name (ARN) entries.

        """
        params = {}
        self.build_list_params(params,
                               container_instances,
                               'containerInstances.member')
        if cluster is not None:
            params['cluster'] = cluster
        return self._make_request(
            action='DescribeContainerInstances',
            verb='POST',
            path='/', params=params)

    def describe_services(self, cluster, services):
        """
        Describes the specified services running in your cluster.

        :type cluster: string
        :param cluster: The name of the cluster that hosts the service you
            want to describe.

        :type services: list of str
        :param services: A list of services you want to describe.
        """
        params = {}
        params["cluster"] = cluster
        self.build_list_params(params,
                               services,
                               'services.member')
        return self._make_request(
            action='DescribeServices',
            verb='POST',
            path='/', params=params)

    def describe_task_definition(self, task_definition):
        """
        Describes a task definition.

        :type task_definition: string
        :param task_definition: The `family` and `revision` (
            `family:revision`) or full Amazon Resource Name (ARN) of the task
            definition that you want to describe.

        """
        params = {'taskDefinition': task_definition, }
        return self._make_request(
            action='DescribeTaskDefinition',
            verb='POST',
            path='/', params=params)

    def describe_tasks(self, tasks, cluster=None):
        """
        Describes a specified task or tasks.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the task you want to describe. If you do not
            specify a cluster, the default cluster is assumed.

        :type tasks: list
        :param tasks: A space-separated list of task UUIDs or full Amazon
            Resource Name (ARN) entries.

        """
        params = {}
        self.build_list_params(params,
                               tasks,
                               'tasks.member')
        if cluster is not None:
            params['cluster'] = cluster
        return self._make_request(
            action='DescribeTasks',
            verb='POST',
            path='/', params=params)

    def discover_poll_endpoint(self, container_instance=None):
        """
        This action is only used by the Amazon EC2 Container Service
        agent, and it is not intended for use outside of the agent.


        Returns an endpoint for the Amazon EC2 Container Service agent
        to poll for updates.

        :type container_instance: string
        :param container_instance: The container instance UUID or full Amazon
            Resource Name (ARN) of the container instance. The ARN contains the
            `arn:aws:ecs` namespace, followed by the region of the container
            instance, the AWS account ID of the container instance owner, the
            `container-instance` namespace, and then the container instance
            UUID. For example, arn:aws:ecs: region : aws_account_id :container-
            instance/ container_instance_UUID .

        """
        params = {}
        if container_instance is not None:
            params['containerInstance'] = container_instance
        return self._make_request(
            action='DiscoverPollEndpoint',
            verb='POST',
            path='/', params=params)

    def list_clusters(self, next_token=None, max_results=None):
        """
        Returns a list of existing clusters.

        :type next_token: string
        :param next_token: The `nextToken` value returned from a previous
            paginated `ListClusters` request where `maxResults` was used and
            the results exceeded the value of that parameter. Pagination
            continues from the end of the previous results that returned the
            `nextToken` value. This value is `null` when there are no more
            results to return.

        :type max_results: integer
        :param max_results: The maximum number of cluster results returned by
            `ListClusters` in paginated output. When this parameter is used,
            `ListClusters` only returns `maxResults` results in a single page
            along with a `nextToken` response element. The remaining results of
            the initial request can be seen by sending another `ListClusters`
            request with the returned `nextToken` value. This value can be
            between 1 and 100. If this parameter is not used, then
            `ListClusters` returns up to 100 results and a `nextToken` value if
            applicable.

        """
        params = {}
        if next_token is not None:
            params['nextToken'] = next_token
        if max_results is not None:
            params['maxResults'] = max_results
        return self._make_request(
            action='ListClusters',
            verb='POST',
            path='/', params=params)

    def list_container_instances(self, cluster=None, next_token=None,
                                 max_results=None):
        """
        Returns a list of container instances in a specified cluster.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the container instances you want to list. If
            you do not specify a cluster, the default cluster is assumed..

        :type next_token: string
        :param next_token: The `nextToken` value returned from a previous
            paginated `ListContainerInstances` request where `maxResults` was
            used and the results exceeded the value of that parameter.
            Pagination continues from the end of the previous results that
            returned the `nextToken` value. This value is `null` when there are
            no more results to return.

        :type max_results: integer
        :param max_results: The maximum number of container instance results
            returned by `ListContainerInstances` in paginated output. When this
            parameter is used, `ListContainerInstances` only returns
            `maxResults` results in a single page along with a `nextToken`
            response element. The remaining results of the initial request can
            be seen by sending another `ListContainerInstances` request with
            the returned `nextToken` value. This value can be between 1 and
            100. If this parameter is not used, then `ListContainerInstances`
            returns up to 100 results and a `nextToken` value if applicable.

        """
        params = {}
        if cluster is not None:
            params['cluster'] = cluster
        if next_token is not None:
            params['nextToken'] = next_token
        if max_results is not None:
            params['maxResults'] = max_results
        return self._make_request(
            action='ListContainerInstances',
            verb='POST',
            path='/', params=params)

    def list_task_definitions(self, family_prefix=None, next_token=None,
                              max_results=None):
        """
        Returns a list of task definitions that are registered to your
        account. You can filter the results by family name with the
        `familyPrefix` parameter.

        :type family_prefix: string
        :param family_prefix: The name of the family that you want to filter
            the `ListTaskDefinitions` results with. Specifying a `familyPrefix`
            will limit the listed task definitions to definitions that belong
            to that family.

        :type next_token: string
        :param next_token: The `nextToken` value returned from a previous
            paginated `ListTaskDefinitions` request where `maxResults` was used
            and the results exceeded the value of that parameter. Pagination
            continues from the end of the previous results that returned the
            `nextToken` value. This value is `null` when there are no more
            results to return.

        :type max_results: integer
        :param max_results: The maximum number of task definition results
            returned by `ListTaskDefinitions` in paginated output. When this
            parameter is used, `ListTaskDefinitions` only returns `maxResults`
            results in a single page along with a `nextToken` response element.
            The remaining results of the initial request can be seen by sending
            another `ListTaskDefinitions` request with the returned `nextToken`
            value. This value can be between 1 and 100. If this parameter is
            not used, then `ListTaskDefinitions` returns up to 100 results and
            a `nextToken` value if applicable.

        """
        params = {}
        if family_prefix is not None:
            params['familyPrefix'] = family_prefix
        if next_token is not None:
            params['nextToken'] = next_token
        if max_results is not None:
            params['maxResults'] = max_results
        return self._make_request(
            action='ListTaskDefinitions',
            verb='POST',
            path='/', params=params)

    def list_services(self, cluster=None, next_token=None, max_results=None):
        """
        Lists the services that are running in a specified cluster.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the services you want to list. If you do not
            specify a cluster, the default cluster is assumed.

        :type next_token: string
        :param next_token: The `next_token` value returned from a previous
            paginated `list_services` request where `max_results` was used and
            the results exceeded the value of that parameter. Pagination
            continues from the end of the previous results that returned the
            `next_token` value. This value is `null` when there are no more
            results to return.

        :type max_results: integer
        :param max_results: The maximum number of task results returned by
            `ListTasks` in paginated output. When this parameter is used,
            `ListTasks` only returns `maxResults` results in a single page
            along with a `nextToken` response element. The remaining results of
            the initial request can be seen by sending another `ListTasks`
            request with the returned `nextToken` value. This value can be
            between 1 and 100. If this parameter is not used, then `ListTasks`
            returns up to 100 results and a `nextToken` value if applicable.
        :type
        """
        params = {}
        if cluster is not None:
            params['cluster'] = cluster
        if next_token is not None:
            params['nextToken'] = next_token
        if max_results is not None:
            params['maxResults'] = max_results
        return self._make_request(
            action='ListServices',
            verb='POST',
            path='/', params=params)

    def get_result(self, result, action):
        return result.get(action + 'Response', {}).get(action + 'Result')

    def list_tasks(self, cluster=None, container_instance=None, family=None,
                   service_name=None, next_token=None, max_results=None):
        """
        Returns a list of tasks for a specified cluster. You can
        filter the results by family name or by a particular container
        instance with the `family` and `containerInstance` parameters.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the tasks you want to list. If you do not
            specify a cluster, the default cluster is assumed..

        :type container_instance: string
        :param container_instance: The container instance UUID or full Amazon
            Resource Name (ARN) of the container instance that you want to
            filter the `ListTasks` results with. Specifying a
            `containerInstance` will limit the results to tasks that belong to
            that container instance.

        :type family: string
        :param family: The name of the family that you want to filter the
            `ListTasks` results with. Specifying a `family` will limit the
            results to tasks that belong to that family.

        :type service_name: string
        :param service_name: The name of the service that you want to filter
            the `ListTasks` results with. Specifying a `serviceName` will limit
            the results to tasks that belong to that service.

        :type next_token: string
        :param next_token: The `nextToken` value returned from a previous
            paginated `ListTasks` request where `maxResults` was used and the
            results exceeded the value of that parameter. Pagination continues
            from the end of the previous results that returned the `nextToken`
            value. This value is `null` when there are no more results to
            return.

        :type max_results: integer
        :param max_results: The maximum number of task results returned by
            `ListTasks` in paginated output. When this parameter is used,
            `ListTasks` only returns `maxResults` results in a single page
            along with a `nextToken` response element. The remaining results of
            the initial request can be seen by sending another `ListTasks`
            request with the returned `nextToken` value. This value can be
            between 1 and 100. If this parameter is not used, then `ListTasks`
            returns up to 100 results and a `nextToken` value if applicable.

        """
        params = {}
        if cluster is not None:
            params['cluster'] = cluster
        if container_instance is not None:
            params['containerInstance'] = container_instance
        if family is not None:
            params['family'] = family
        if service_name is not None:
            params['serviceName'] = service_name
        if next_token is not None:
            params['nextToken'] = next_token
        if max_results is not None:
            params['maxResults'] = max_results
        return self._make_request(
            action='ListTasks',
            verb='POST',
            path='/', params=params)

    def register_container_instance(self, cluster=None,
                                    instance_identity_document=None,
                                    instance_identity_document_signature=None,
                                    total_resources=None):
        """
        This action is only used by the Amazon EC2 Container Service
        agent, and it is not intended for use outside of the agent.


        Registers an Amazon EC2 instance into the specified cluster.
        This instance will become available to place containers on.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that you want to register your container instance with.
            If you do not specify a cluster, the default cluster is assumed..

        :type instance_identity_document: string
        :param instance_identity_document:

        :type instance_identity_document_signature: string
        :param instance_identity_document_signature:

        :type total_resources: list
        :param total_resources:

        """
        params = {}
        if cluster is not None:
            params['cluster'] = cluster
        if instance_identity_document is not None:
            params['instanceIdentityDocument'] = instance_identity_document
        if instance_identity_document_signature is not None:
            params['instanceIdentityDocumentSignature'] = instance_identity_document_signature
        if total_resources is not None:
            self.build_complex_list_params(
                params, total_resources,
                'totalResources.member',
                ('name', 'type', 'doubleValue', 'longValue', 'integerValue', 'stringSetValue'))
        return self._make_request(
            action='RegisterContainerInstance',
            verb='POST',
            path='/', params=params)

    def build_complex_object_params(self, params, items, label):
        """Serialize a list of structures.

        For example::

            items = [('foo', 'bar', 'baz'), ('foo2', 'bar2', 'baz2')]
            label = 'ParamName.member'
            names = ('One', 'Two', 'Three')
            self.build_complex_list_params(params, items, label, names)

        would result in the params dict being updated with these params::

            ParamName.member.1.One = foo
            ParamName.member.1.Two = bar
            ParamName.member.1.Three = baz

            ParamName.member.2.One = foo2
            ParamName.member.2.Two = bar2
            ParamName.member.2.Three = baz2

        :type params: dict
        :param params: The params dict.  The complex list params
            will be added to this dict.

        :type items: list of tuples
        :param items: The list to serialize.

        :type label: string
        :param label: The prefix to apply to the parameter.

        :type names: tuple of strings
        :param names: The names associated with each tuple element.

        """
        def handle_item(label, item):
            for key, value in item.items():
                full_key = '%s.%s' % (label, key)
                if type(value) == list:
                    handle_list(full_key, value)
                elif value in (True, False):
                    params[full_key] = json.dumps(value)
                else:
                    params[full_key] = value

        def handle(label, item):
            if type(item) == list:
                _handle_list(label, item)
                return True
            elif type(item) == dict:
                _handle_dict(label, item)

        def _handle_list(label, items):
            for i, item in enumerate(items, 1):
                current_prefix = '%s.member.%s' % (label, i)
                handle(current_prefix, item)
                if type(item) == list:
                    _handle_list(current_prefix, item)
                elif type(item) == dict:
                    _handle_dict(current_prefix, item)
                else:
                    params[current_prefix] = item

        def _handle_dict(label, item):
            for key, value in item.items():
                full_key = '%s.%s' % (label, key)
                if type(value) == list:
                    _handle_list(full_key, value)
                elif value in (True, False):
                    params[full_key] = json.dumps(value)
                else:
                    params[full_key] = value

        _handle_list(label, items)

    def register_task_definition(self, family, container_definitions):
        """
        Registers a new task definition from the supplied `family` and
        `containerDefinitions`.

        :type family: string
        :param family: You can specify a `family` for a task definition, which
            allows you to track multiple versions of the same task definition.
            You can think of the `family` as a name for your task definition.

        :type container_definitions: list
        :param container_definitions: A list of container definitions in JSON
            format that describe the different containers that make up your
            task.

        """
        params = {'family': family, }
        self.build_complex_object_params(
            params, container_definitions,
            'containerDefinitions')
        return self._make_request(
            action='RegisterTaskDefinition',
            verb='POST',
            path='/', params=params)

    def run_task(self, task_definition, cluster=None, overrides=None,
                 count=None):
        """
        Start a task using random placement and the default Amazon ECS
        scheduler. If you want to use your own scheduler or place a
        task on a specific container instance, use `StartTask`
        instead.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that you want to run your task on. If you do not
            specify a cluster, the default cluster is assumed..

        :type task_definition: string
        :param task_definition: The `family` and `revision` (
            `family:revision`) or full Amazon Resource Name (ARN) of the task
            definition that you want to run.

        :type overrides: dict
        :param overrides:

        :type count: integer
        :param count: The number of instances of the specified task that you
            would like to place on your cluster.

        """
        params = {'taskDefinition': task_definition, }
        if cluster is not None:
            params['cluster'] = cluster
        if overrides is not None:
            params['overrides'] = overrides
        if count is not None:
            params['count'] = count
        return self._make_request(
            action='RunTask',
            verb='POST',
            path='/', params=params)

    def start_task(self, task_definition, container_instances, cluster=None,
                   overrides=None):
        """
        Starts a new task from the specified task definition on the
        specified container instance or instances. If you want to use
        the default Amazon ECS scheduler to place your task, use
        `RunTask` instead.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that you want to start your task on. If you do not
            specify a cluster, the default cluster is assumed..

        :type task_definition: string
        :param task_definition: The `family` and `revision` (
            `family:revision`) or full Amazon Resource Name (ARN) of the task
            definition that you want to start.

        :type overrides: dict
        :param overrides:

        :type container_instances: list
        :param container_instances: The container instance UUIDs or full Amazon
            Resource Name (ARN) entries for the container instances on which
            you would like to place your task.

        """
        params = {'taskDefinition': task_definition, }
        self.build_list_params(params,
                               container_instances,
                               'containerInstances.member')
        if cluster is not None:
            params['cluster'] = cluster
        if overrides is not None:
            params['overrides'] = overrides
        return self._make_request(
            action='StartTask',
            verb='POST',
            path='/', params=params)

    def stop_task(self, task, cluster=None):
        """
        Stops a running task.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the task you want to stop. If you do not
            specify a cluster, the default cluster is assumed..

        :type task: string
        :param task: The task UUIDs or full Amazon Resource Name (ARN) entry of
            the task you would like to stop.

        """
        params = {'task': task, }
        if cluster is not None:
            params['cluster'] = cluster
        return self._make_request(
            action='StopTask',
            verb='POST',
            path='/', params=params)

    def submit_container_state_change(self, cluster=None, task=None,
                                      container_name=None, status=None,
                                      exit_code=None, reason=None,
                                      network_bindings=None):
        """
        This action is only used by the Amazon EC2 Container Service
        agent, and it is not intended for use outside of the agent.


        Sent to acknowledge that a container changed states.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the container.

        :type task: string
        :param task: The task UUID or full Amazon Resource Name (ARN) of the
            task that hosts the container.

        :type container_name: string
        :param container_name: The name of the container.

        :type status: string
        :param status: The status of the state change request.

        :type exit_code: integer
        :param exit_code: The exit code returned for the state change request.

        :type reason: string
        :param reason: The reason for the state change request.

        :type network_bindings: list
        :param network_bindings: The network bindings of the container.

        """
        params = {}
        if cluster is not None:
            params['cluster'] = cluster
        if task is not None:
            params['task'] = task
        if container_name is not None:
            params['containerName'] = container_name
        if status is not None:
            params['status'] = status
        if exit_code is not None:
            params['exitCode'] = exit_code
        if reason is not None:
            params['reason'] = reason
        if network_bindings is not None:
            self.build_complex_list_params(
                params, network_bindings,
                'networkBindings.member',
                ('bindIP', 'containerPort', 'hostPort'))
        return self._make_request(
            action='SubmitContainerStateChange',
            verb='POST',
            path='/', params=params)

    def submit_task_state_change(self, cluster=None, task=None, status=None,
                                 reason=None):
        """
        This action is only used by the Amazon EC2 Container Service
        agent, and it is not intended for use outside of the agent.


        Sent to acknowledge that a task changed states.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that hosts the task.

        :type task: string
        :param task: The task UUID or full Amazon Resource Name (ARN) of the
            task in the state change request.

        :type status: string
        :param status: The status of the state change request.

        :type reason: string
        :param reason: The reason for the state change request.

        """
        params = {}
        if cluster is not None:
            params['cluster'] = cluster
        if task is not None:
            params['task'] = task
        if status is not None:
            params['status'] = status
        if reason is not None:
            params['reason'] = reason
        return self._make_request(
            action='SubmitTaskStateChange',
            verb='POST',
            path='/', params=params)

    def update_service(self, cluster=None, desired_count=None,
                       service=None, task_definition=None):
        """
        Modify the desired count or task definition used in a service.

        You can add to or subtract from the number of instantiations of a task
        definition in a service by specifying the cluster that the service is
        running in and a new `desired_count` parameter.

        You can use `update_service` to modify your task definition and deploy
        a new version of your service, one task at a time. If you modify the
        task definition with `update_service`, Amazon ECS spawns a task with
        the new version of the task definition and then stops an old task after
        the new version is running. Because `update_service` starts a new
        version of the task before stopping an old version, your cluster must
        have capacity to support one more instantiation of the task when
        `update_service` is run. If your cluster cannot support another
        instantiation of the task used in your service, you can reduce the
        desired count of your service by one before modifying the task
        definition.

        :type cluster: string
        :param cluster: The short name or full Amazon Resource Name (ARN) of
            the cluster that you want to run your service on. If you do not
            specify a cluster, the default cluster is assumed.

        :type desired_count: integer
        :param desired_count: The number of instantiations of the specified
            task definition that you would like to place and keep running on
            your cluster.

        :type service: string
        :param service: The name of the service that you want to update.

        :type task_definition: string
        :param task_definition: The `family` and `revision` (`family:revision`)
            or full Amazon Resource Name (ARN) of the task definition that you
            want to run in your service.
        """
        params = {}
        if service is not None:
            params['service'] = service
        if cluster is not None:
            params['cluster'] = cluster
        if desired_count is not None:
            params['desiredCount'] = desired_count
        if task_definition is not None:
            params['taskDefinition'] = task_definition

        return self._make_request(
            action='UpdateService',
            verb='POST',
            path='/', params=params)

    def _make_request(self, action, verb, path, params):
        params['ContentType'] = 'JSON'
        response = self.make_request(action=action, verb='POST',
                                     path='/', params=params)
        body = response.read().decode('utf-8')
        boto.log.debug(body)
        if response.status == 200:
            body = json.loads(body)
            return body.get(action + 'Response', {}).get(action + 'Result', None)
        else:
            json_body = json.loads(body)
            fault_name = json_body.get('Error', {}).get('Code', None)
            exception_class = self._faults.get(fault_name, self.ResponseError)
            raise exception_class(response.status, response.reason,
                                  body=json_body)
