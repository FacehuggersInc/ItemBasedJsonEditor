project writen in python 3.12.4

This project was meant to handle and easily modify JSON for a lot of game-related items, making it easy to create new items and adjust JSON.

JSON files can only be accepted by this application if they follow this data structure in JSON: root (dict) > key : list [dict, dict, dict, ...]. This is currently a strict requirement; it will not load if any key in the root does not have a list value, and if any item within that list is not another dict.

```json
{
  "weapons": [
    {},
    {},
    {}
  ]
}
```
These files can include multiple root-level keys (like weapons) with easy switching between them AND have the ability to also load multiple files into the App without issue when saving them.

### Key Features
#### Item Editing
* Easily modify key-value pairs within any item.
* Easily copy entire structures
* Easily paste new JSON or list into a string field to auto-convert to dict or list
* Key-Value fields auto-convert to detected type (int, float, str ...) so there are no type conversion issues
* Create completely new items or duplicate existing ones
* Apply global modifications to make all items share the same data structure.
* Simplifies mass editing of JSON-based item lists.

#### Source Manager
* Organize data sources as folders called sources.
* Each source can be configured with modifications:
  * Path Splice – Replace parts of file paths dynamically when selecting files from the source.
  * Random – Randomly select a file from the source folder.
  * None – Use files directly from the source without modification.
* Provides a clean way to add files paths to any key-value pair
* Includes Image Previews and a Remembrance of what preview (source file) was there even when using Path Splicing.

This project is open to suggestions and, of course, to report issues.







