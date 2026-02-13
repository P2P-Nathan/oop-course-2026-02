# Key items for assignment

## Assignment is a backend API of a game
Its not the frontend, just the API

## Look for opportunities to create a custom container class
It came up in the marketplace example and was related to a couple of the items created for class like Bag and WithdrawableStack

## Look for pattern opportunities
Flyweight came up a couple times in class, as well as factory pattern, pub/sub came up as well, look at the listing file.  Look at the PubSub example in user in the marketplace to track the activity

## Add validation for the methods and actions
Its good practice but also shows an understanding of what is going on.  Use `if` to check items that you expect to see.  Assert is only for internal checking to make sure that you've written it right.  Assert can be used for cool testing performance, and example is in the marketplace.

## Encapsulation errors
Encapsulate items correctly for the single responsibility, expose the correct state of the game and correct methods to operate the game.  Don't over expose data that isn't required but make everything accessible safely.  You should be able to see the methods you need to work but not the internal methods we shouldn't use.  Don't let the user modify things that they shouldn't be able to, but they might be able to see them through a proxy for example.

## Modules are a source of Single Responsibility
Classes that have a strong relationship should be in the same module, and modules should be loosely coupled.  SRP applies to the modules, so the interfaces, protocols, and types should be in the correct module for where they are used.  Items like descriptors and utilities can be in a utilities module or a descriptors module.

# AVOID these items

## Use of `super()`
This gets the next item in the MRO and it may not get the class which you are intending to get.  Use the class name directly to specify a method from the base class.  Professor was big on `super()` being a dangerous choice that results in lots of errors.  The only case the other way is cooperative design, which can be seen in the `using_super.py` file.  Super doesn't work on attributes.

## Use excess abstract classes
Prefer the use of `protocol` over an abstract unless there is shared logic which is required for the abstract class.  The buyer and seller in our marketplace could share a base MarketplaceUserABC.  

## Use of the `:=` walrus operator without reason or comment
There was a debate in the python community and this is a big debatable but does have a function

## Multi-inheritance
It was done in class as an example of functionality, however the professor mentioned that he wouldn't ever use them in production


# ALWAYS look for these

## Opportunities to remove O(n) level operations
Removing an item from a list can be expensive for example.  Take a look at the WithdrawableStack and how the index and deletable classes are used to improve performance.

## `__slots__ = ()`
Interfaces and mixins must always declare slots with an explicit list of properties.  If not used then the `__dict__` will be created and use excess space.

## Correct use of `__new__` and `__init__`
New should be used most of the time, and always when creating an object which isn't using multiple inheritance.  When using true multiple inheritance create the blank object with runtime and run the initializers for all parent classes and hope they don't collide.  Look at the buffer example.

Init is also acceptable for use when creating new error types

## Understanding of MRO and conflicts 
Python multi inheritance types overwrite each other with the MRO so make sure that these items are operating as intended

## Interesting data structure options
Reusable data structures that have benefit and the professor finds interesting will be beneficial for the project.  Using the Bag or Withdrawable stack in the same way isn't worth the extra points.  Using these items for composition to create the solution is good too.  This was specifically called out before we created the Withdrawable stack in class, so that might have hints.

## Good use of literals
When applicable use a literal over an enum for example as they are newer and well supported.  Look for other good opportunities for literals

## Correct use of inheritance and composition
Following the L in the SOLID principals it should only overwrite or inherit from if it is the same (Liskov principle).  See the exercises and the WithdrawableStack for examples

## Use `@dataclass` for simple data structures
Don't use a full class if all you need to do is just store low level data.  A dataclass can be also be frozen and have its slots set, see the bids and withdrawable stack items.


# Use for legibility and quality

## Type aliases
These allow for something like `int` to be aliased as `Byte` so that those reading the code know which is an index and which is a byte of data.  Also look for `ContiguousSlice` in the buffer example.  Sometimes readability is key, look at the Username type alias over str

## Custom errors
See the marketplace for an example, a custom state error was created for transitions of listings in the marketplace.  This included the data key to the transition.

## Keyword arguments
These are powerful and modern, if there is an opportunity to effectively add them without adding excess work suggest and document it.

## Use of facades
If used in a package, only export the facade class.  It is a great way to create a single entry point to the code.

## Use a decorator pattern to apply consistency
A good example is the way Auth is done in .NET or the python example we have in state transitions in Listings which checks to see if it is in an applicable state

## Exceptions of nested types
Look at the stack examples, by creating and organizing our error types we can catch items more controllably 

## Document invariants 
Use to describe what is known and expected of a method

## `__setattr__` or `__setitem__` change how attributes work
Look at the `attribute_lookup.py` for creative use of how this works and its interface/protocol



# The regular python way

## Errors on empty stack
Stacks that are empty will return an error when operated against

## Use `not` in the special cases
It will use `__len__` for collections to test it they are valid, good way to validate if item is good

## Use `in` to access collection
Good to check if an item is in the collection

## Use `del` to remove items or attributes
Is the standard way to remove attributes or items in a collection

## Look to built-in operations for inspiration
Many examples when building items referenced that it was done the same way as the system functionality, if this behavior is available, we shouldn't make our own crazy way.

## Use the double underscore dunder methods correctly
Implement things like `__len__` and other built in methods so that the built in functions like `len()` work correctly on the object.  Details at https://www.pythonmorsels.com/every-dunder-method/
