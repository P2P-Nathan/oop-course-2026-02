# Key items for assignment

## Assignment is a backend API of a game
Its not the frontend, just the API

# AVOID these items

## Use of `super()`
This gets the next item in the MRO and it may not get the class which you are intending to get.  Use the class name directly to specify a method from the base class.  Professor was big on `super()` being a dangerous choice that results in lots of errors.

## Use of abstract classes
Prefer the use of `protocol` over an abstract unless there is shared logic which is required for the abstract class.


# ALWAYS look for these

## Opportunities to remove O(n) level operations
Removing an item from a list can be expensive for example.  Take a look at the WithdrawableStack and how the index and deletable classes are used to improve performance.

## `__slots__ = ()`
Interfaces and mixins must always declare slots with an explicit list of properties.  If not used then the `__dict__` will be created and use excess space.

## Correct use of `__new__` and `__init__`
New should be used most of the time, and always when creating an object which isn't using multiple inheritance.  When using true multiple inheritance create the blank object with runtime and run the initiallizers for all parent classes and hope they don't collide.  Look at the buffer example.

Init is also acceptable for use when creating new error types

## Understanding of MRO and conflicts 
Python multi inheritence types overwrite eachother with the MRO so make sure that these items are operating as intended

## Interesting data structure options
Reusable data structures that have benefit and the professor finds interesting will be benefitial for the project.  Using the Bag or Withdrawable stack in the same way isn't worth the extra points.  Using these items for composition to create the solution is good too.  This was specifically called out before we created the Withdrawable stack in class, so that might have hints.

## Good use of literals
When applicable use a literal over an enum for example as they are newer and well supported.  Look for other good opportunities for literals

## Correct use of inheritance and composition
Following the L in the SOLID prinicipals it should only overwrite or inherit from if it is the same (Liskov principle).  See the excercises and the WithdrawableStack for examples

## Use `@dataclass` for simple data structures
Don't use a full class if all you need to do is just store low level data.  A dataclass can be also be frozen and have its slots set, see the bids and withdrawable stack items.


# Use for legibility and quality

## Type aliases
These allow for something like `int` to be aliased as `Byte` so that those reading the code know which is an index and which is a byte of data.  Also look for `ContiguousSlice` in the buffer example

## Custom errors
See the marketplace for an example, a custom state error was created for transitions of listings in the marketplace.  This included the data key to the transition.

## Keyword arguments
These are powerful and modern, if there is an opportunity to effectivly add them without adding excess work suggest and document it.

## Use of facades
If used in a package, only export the facade class.  It is a great way to create a single entry point to the code.

## Use a decorator pattern to apply consistency
A good example is the way Auth is done in .NET or the python example we have in state transitions in Listings which checks to see if it is in an applicable state

## Exceptions of nested types
Look at the stack examples, by creating and organizing our error types we can catch items more controllably 

## Document invariants 
Use to describe what is known and expected of a method



# The regular python way

## Errors on empty stack
Stacks that are empty will return an error when operated against

## Use `not` in the special cases
It will use `__len__` for collections to test it they are valid, good way to validate if item is good

## Use `in` to access collection
Good to check if an item is in the collection

## Use `del` to remove items or attributes
Is the standard way to remove attributes or items in a collection