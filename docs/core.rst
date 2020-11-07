Core Models
===============


Verse
--------
A key design feature of D-Codex is that it is base on the smallest textual unit appropriate for the manuscript type. 
This abstract class is called a ``Verse``. Each ``Verse`` object ought only occur once per manuscript. 
For each possible verse, there must be an instance of a child-class of Verse saved in the database. 
Sub-classes of ``Verse`` are required to complete a method to return a reference string for each verse, such as 'Matthew 1:1' 
(with an option for an abbreviated form, e.g. 'Mt 1:1'). There also needs to be a method to have a unique string to be used in a URL. 
The default implementation of this is simply the reference string with white space removed. 
This string must uniquely match with only that instance of Verse in the child-class. 
Furthermore, a class method must be defined which is able to locate any verse from a string. 
Another similar method is required to locate a ``Verse`` instance from a Python dictionary. 
The keys for the dictionary are determined by the child class. 
As a minimum this method must be able to interpret the unique reference string (with any abbreviation option if appropriate). 
This function is used to find verses embedded in a URL. 
Care needs to be taken when defining a sub-class of ``Verse`` that the uniqueness property is respected. 
This property means that D-Codex is not a suitable software package for all texts, but only those with a standard versification system.


Manuscript
--------------

The abstract class that brings together all the elements in a document is called the ``Manuscript`` class. 
In the base Manuscript class, a descriptive name can be set (e.g. 'Codex Sinaiticus Arabicus') and a siglum (e.g. 'CSA'). 
The siglum is used in the URLs for webpages to do with the manuscript and must be unique. 
A child class needs to specify a method to return the appropriate ``Verse`` class and also the ``Transcription`` class. 
The ``Manuscript`` class is responsible for navigation in the manuscript. 
This involves needing to be able to take any verse and find the next or previous verse. 
It also needs to implement a method to find distance between the start of one verse and the start of another. 
Helper functions are implemented in the base class to do many common tasks at the manuscript level (such as to create a list of all transcriptions).

Transcription and Markup
----------------------------

The ``Transcription`` class stores the text of a transcribed verse and associates it with the manuscript and verse instances. 
It can also have a reference to a ``Markup`` object. The ``Markup`` class is responsible for four tasks:

	1. Providing a widget text box for transcribing the text of the verse in the user interface.
	2. Regularising the transcription text for string comparison.
	3. Displaying the text cleanly in HTML.
	4. Converting to TEI XML markup.

A default markup object can be assigned to a manuscript and specific markup objects can be assigned to individual verses. 
Though ideally, one would wish for a consistent markup scheme for any particular manuscript, there are situations where multiple markup schemes could be operating. 

..
    For the Arabic transcriptions in this thesis, they were written using a `SimpleArabicMarkup' class. It  provides a basic text box for transcription in the user interface. For regularisation, the text is standardised to ignore inconsequential orthographic differences between the two manuscripts. This means ignoring punctuation, short vowels, the diacritics on a \textit{tāʾ marbūṭa} and different ways of writing a final \textit{yāʾ} or \textit{ʾalif}. 


Location
--------------

The ``Location`` class joins a manuscript and verse object and associates them with the pixel coordinates on a 
facsimile image which corresponds to the beginning of the verse. DCodex stores these values as a 
proportion of the width or height of the image and so the values are between 0 and 1. 
For left-to-right languages, this means to the top-left of the first character in the verse, and for right-to-left languages such as Arabic, 
his means the top-right of the first character. 

Not all the locations of each verse need to be transcribed. 
Once the location of at least two verses is transcribed, D-Codex can estimate the location of any other verse. 
To do this, we refer to two quantities: the textual mass between two verses and the spatial distance between the locations of the two verses.


Family and Affiliation
---------------------------------

One challenge with working with complex manuscript traditions is the presence of block-mixture. 
D-Codex has a powerful and extensible means of defining the relationship between the texts of manuscripts at certain points. 
Manuscripts can be grouped in an instance of a ``Family`` class. Each ``Family`` object must be given a string as a name. 
Manuscripts can be members of the ``Family`` group by means of an instance of an ``Affiliation`` class. 
The abstract ``AffiliationBase`` object combines a list of families as well as a list of manuscripts. 
Each subclass of ``AffiliationBase`` must provide a method defining whether or not the affiliation is *active* at any particular verse. 
If the affiliation is active then all the manuscripts in that affiliation are regarded as members of the list of associated families at any particular verse. 

The most basic subclass of ``AffiliationBase`` is ``AffiliationAll`` which simply states that the affiliation is active for all verses. 
All manuscripts in this affiliation will be always associated with all families listed in it. 

Another subclass of `AffiliationBase` is ``AffiliationVerses`` to which the user can give a list of verses at which the affiliation is active and elsewhere it is not. 
A similar subclass is `AffiliationRange`` where the user can give a starting verse and an ending verse and the affiliation is active within this range (inclusively).

Not every affiliation object needs to have manuscripts listed in it, meaning that the affiliation object would just be applying to the families associated with it.
