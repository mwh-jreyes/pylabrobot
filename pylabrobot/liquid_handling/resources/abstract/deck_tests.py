import unittest

from pylabrobot.liquid_handling.resources.abstract.deck import Coordinate, Deck, Resource


class DeckTests(unittest.TestCase):
  """ Tests for the `Deck` class. """

  def test_assign_resource(self):
    deck = Deck()
    resource = Resource(name="resource", size_x=1, size_y=1, size_z=1)
    deck.assign_child_resource(resource, location=Coordinate.zero())
    self.assertEqual(deck.get_resource("resource"), resource)

  def test_assign_resource_twice(self):
    deck = Deck()
    resource = Resource(name="resource", size_x=1, size_y=1, size_z=1)
    deck.assign_child_resource(resource, location=Coordinate.zero())
    with self.assertRaises(ValueError):
      deck.assign_child_resource(resource, location=Coordinate.zero())

  def test_clear(self):
    deck = Deck()
    resource = Resource(name="resource", size_x=1, size_y=1, size_z=1)
    deck.assign_child_resource(resource, location=Coordinate.zero())
    deck.clear()
    with self.assertRaises(ValueError):
      deck.get_resource("resource")
