from __future__ import annotations

from typing import List, Optional

from .coordinate import Coordinate


class Resource:
  """ Base class for deck resources.

  Args:
    name: The name of the resource.
    size_x: The size of the resource in the x-direction.
    size_y: The size of the resource in the y-direction.
    size_z: The size of the resource in the z-direction.
    location: The location of the resource.
    category: The category of the resource, e.g. `tips`, `plate_carrier`, etc.
  """

  def __init__(
    self,
    name: str,
    size_x: float,
    size_y: float,
    size_z: float,
    location: Coordinate = Coordinate(None, None, None),
    category: str = None
  ):
    self.name = name
    self._size_x = size_x
    self._size_y = size_y
    self._size_z = size_z
    self.location = location
    self.category = category

    self.parent: Optional[Resource] = None
    self.children: List[Resource] = []

  def serialize(self) -> dict:
    """ Serialize this resource. """
    return dict(
      name=self.name,
      type=self.__class__.__name__,
      size_x=self._size_x,
      size_y=self._size_y,
      size_z=self._size_z,
      location=self.location.serialize(),
      category=self.category or "unknown"
    )

  def __eq__(self, other):
    return (
      isinstance(other, Resource) and
      self.name == other.name and
      self.get_size_x() == other.get_size_x() and
      self.get_size_y() == other.get_size_y() and
      self.get_size_z() == other.get_size_z() and
      self.location == other.location and
      self.category == other.category
    )

  def get_absolute_location(self):
    """ Get the absolute location of this resource, probably within the
    :class:`pyhamilton.liquid_handling.resources.abstract.Deck`. """
    if self.parent is None:
      return self.location
    return self.parent.get_absolute_location() + self.location

  def get_size_x(self) -> float:
    return self._size_x

  def get_size_y(self) -> float:
    return self._size_y

  def get_size_z(self) -> float:
    return self._size_z

  def assign_child_resource(self, resource: Resource, **kwargs):
    """ Assign a child resource to this resource.

    Will use :meth:`~Resource.resource_assigned_callback` to notify the parent of the assignment,
    if parent is not `None`.  If the resource to be assigned has child resources, this method will
    be called for each of them.
    """

    self.resource_assigned_callback(resource) # call callbacks first.

    for child in resource.get_all_children():
      self.resource_assigned_callback(child)

    resource.parent = self
    self.children.append(resource)

  def unassign_child_resource(self, resource: Resource):
    """ Unassign a child resource from this resource.

    Will use :meth:`~Resource.resource_unassigned_callback` to notify the parent of the
    unassignment, if parent is not `None`.
    """

    if resource not in self.children:
      raise ValueError(f"Resource with name '{resource.name}' is not a child of this resource "
                       f"('{self.name}').")

    for child in resource.get_all_children():
      self.resource_unassigned_callback(child)

    self.resource_unassigned_callback(resource) # call callbacks first.
    resource.parent = None
    self.children.remove(resource)

  def unassign(self):
    """ Unassign this resource from its parent. """
    if self.parent is not None:
      self.parent.unassign_child_resource(self)

  def resource_assigned_callback(self, resource):
    """ Called when a resource is assigned to this resource.

    May be overridden by subclasses.

    May raise an exception if the resource cannot be assigned to this resource.

    Args:
      resource: The resource that was assigned.
    """

    if self.parent is not None:
      self.parent.resource_assigned_callback(resource)

  def resource_unassigned_callback(self, resource):
    """ Called when a resource is unassigned from this resource.

    May be overridden by subclasses.

    May raise an exception if the resource cannot be unassigned from this resource.

    Args:
      resource: The resource that was unassigned.
    """

    if self.parent is not None:
      self.parent.resource_unassigned_callback(resource)

  def get_all_children(self) -> List[Resource]:
    """ Recursively get all children of this resource. """
    children = self.children.copy()
    for child in self.children:
      children += child.get_all_children()
    return children

  def get_resource(self, name: str) -> Optional[Resource]:
    """ Get a resource by name. """
    if self.name == name:
      return self

    for child in self.children:
      if child.name == name:
        return child

      resource = child.get_resource(name)
      if resource is not None:
        return resource

    return None
