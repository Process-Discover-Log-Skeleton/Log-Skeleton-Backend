"""Base class for the log-skeleton relationship implementations."""

from enum import Enum
import os
import uuid
import itertools
from src.components.util.xes_importer import XES_Importer

# XES-concept extension. General identifier field of an event.
__CONCEPT_NAME__ = 'concept:name'

TRACE_START = {__CONCEPT_NAME__: uuid.uuid4().hex}
TRACE_END = {__CONCEPT_NAME__: uuid.uuid4().hex}


class Relationship:
    """Base class for the log-skeleton relationship implementations.

    This class can be inhertited to implement the relationship algorithms.
    It provides different kinds of helper functions to make the
    implementation of the relationship algorithm as easy as possible.
    """

    class Mode (Enum):
        FORALL = 0
        EXISTS = 1

    def __init__(self, log):
        """Store the traces."""
        self.log = log
        self.activities = self.extract_activities()

        self.include_extenstions = False
        self.mode = Relationship.Mode.FORALL

        for i in range(len(log)):
            log[i] = self.extended_trace(log[i])


    def extract_activities(self):
        """Extract the activity set from the log."""
        activities = set()

        for trace in self.log:
            for activity in trace:
                activities.add(self.activity_concept_name(activity))

        return activities

    def extended_trace(self, trace):
        """Convert a trace to the extended trace."""
        return [TRACE_START] + trace._list + [TRACE_END]

    # Activity related functions
    def activity_concept_name(self, activity) -> str:
        """Extract the concept:name of an activity."""
        return activity[__CONCEPT_NAME__]

    def is_start(self, activity) -> bool:
        """Determine whether an activity is the start activity."""
        return activity == self.activity_concept_name(TRACE_START)

    def is_end(self, activity) -> bool:
        """Determine whether an activity is the end activity."""
        return activity == self.activity_concept_name(TRACE_END)

    def is_extension_activity(self, activity) -> bool:
        """Determine whether an activity is one of the extension activities."""
        return self.is_start(activity) or self.is_end(activity)

    # Trace related functions
    def is_empty(self, trace) -> bool:
        """Return whether the trace is empty."""
        return len(trace) == 0

    def project_trace(self, trace, elements):
        """Project the trace to a given set of activities."""
        res = filter(
            lambda ac: self.activity_concept_name(ac) in elements, trace)

        return list(map(lambda ac: self.activity_concept_name(ac), res))

    def subtrace_count(self, trace, subtrace):
        """Count the number of occurences of subtrace in trace"""
        if len(subtrace) == 0:
            return 0

        count = 0

        tr = list(map(lambda ac: self.activity_concept_name(ac), trace))

        for index in range(len(tr) - len(subtrace) + 1):
            slice = tr[index:index + len(subtrace)]

            if subtrace == slice:
                count += 1

        return count


    def first(self, trace):
        """Return the first activity."""
        return trace[0]

    def last(self, trace):
        """Return the last activity."""
        return trace[-1]

    def count(self, trace):
        """Return the number of activity in that one trace."""
        return len(trace)

    def create_relation_superset(self):
        """Creates the crossproduct of the actvities"""
        # trace = [a, b, c]
        # trace x trace = [(a, a), (a, b), ..., (c, a), (c, b), (c, c)]
        return itertools.product(self.activities, self.activities)

    def apply(self):
        """Implement a relationship algorithm."""
        results = []

        source = self.create_relation_superset()

        if self.mode == Relationship.Mode.FORALL: # For all condition
            for a1, a2 in source:
                res = True
                for trace in self.log:
                    res = res and self.apply_to_trace(trace, a1, a2)

                    if not res:
                        break

                if res:
                    results.append((a1, a2))

        else: # Exists condition
            for a1, a2 in source:
                res = False
                for trace in self.log:
                    res = res or self.apply_to_trace(trace, a1, a2)

                    if res:
                        break

                if res:
                    results.append((a1, a2))

        return results

    def apply_to_trace(self, trace, a1, a2) -> bool:
        """Apply the matching algorithm to each pair of activities."""
        if self.activity_pair_matches(trace, a1, a2):

            if not self.include_extenstions and (self.is_extension_activity(a1) \
                    or self.is_extension_activity(a2)):
                return False

            return True

        return False

    def activity_pair_matches(self, trace, activity1, activity2) -> bool:
        """Determine if the given pair of activities is in the result."""
        raise NotImplementedError


if __name__ == "__main__":
    importer = XES_Importer()

    path = os.path.join(
        os.path.dirname(__file__), '../../../res/logs/running-example.xes')

    log = importer.import_file(path)

    print(log[0])
    print('Activity')
    print(log[0][0])
