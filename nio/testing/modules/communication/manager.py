from nio.modules.communication.matching import matches


class PubSubManager(object):

    """ A Communication manager to allow simple pub/sub in unit tests

    This works with the unit-test Publisher and Subscriber to allow data
    to be published and subscribed to in the same process.
    """

    publishers = {}
    subscribers = []

    @classmethod
    def add_publisher(cls, publisher):
        """ Add a publisher to this manager.

        This will register the topic of the publisher with any matching
        Subscribers so that they will get called when data is published on
        this publisher.
        """
        cls.publishers[publisher] = []
        for subscriber in cls.subscribers:
            if cls._matches(subscriber.topic, publisher.topic):
                cls.publishers[publisher].append(subscriber)

    @classmethod
    def remove_publisher(cls, publisher):
        """ De-register a publisher with this manager """
        if publisher in cls.publishers:
            del cls.publishers[publisher]

    @classmethod
    def add_subscriber(cls, subscriber):
        """ Add a subscriber to this manager and subscribe to relevant data.

        This will add this subscriber's callback to any registered publishers
        whose topic match.
        """
        cls.subscribers.append(subscriber)
        for publisher in cls.publishers.keys():
            if cls._matches(subscriber.topic, publisher.topic):
                cls.publishers[publisher].append(subscriber)

    @classmethod
    def remove_subscriber(cls, subscriber):
        """ De-register the subscriber with this manager """
        for publisher_callbacks in cls.publishers.values():
            if subscriber in publisher_callbacks:
                publisher_callbacks.remove(subscriber)
        cls.subscribers.remove(subscriber)

    @classmethod
    def send(cls, publisher, signals):
        """ Send data from a publisher to any subscribed callbacks """
        for subscriber in cls.publishers[publisher]:
            subscriber.handler(signals)

    @classmethod
    def _matches(cls, sub_topic, pub_topic):
        """ Use a simple matching algorithm imitating wildcards on a path

        Args:
            sub_topic (str): sub_topic to match can contain wildcards (*)
            pub_topic (str): publisher topic

        Returns:
            True if they match, False otherwise
        """
        return matches(sub_topic, pub_topic)
