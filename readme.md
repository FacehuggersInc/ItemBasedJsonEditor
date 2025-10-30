This project was meant to handle and easily modifiy JSON for a lot of items, making it easy to make new items and adjust JSON. 

JSON files can only be accepted by this Application if they follow this data Structure in JSON. root (dict) > key : list [dict, dict, dict, ...].

```json
{
  "weapons": [
    {},
    {},
    {}
  ]
}
```
These files can include multiple root-level keys (like weapons) with easy switching between them AND has the ability to also load multiple files into the App without issue on saving them.

### Key Features
#### Item Editing
* Easily modify key-value pairs within any item.
* Easily copy and paste JSON directly from Key Value Pairs or the enitre structure
* Create completly new items or duplicate existing ones
* Apply global modifications to make all items share the same data structure.
* Simplifies mass editing of JSON-based item lists.

#### Source Manager
* Organize data sources as folders called sources.
* Each source can be configured with modifications:
  * Path Splice – Replace parts of file paths dynamically when selecting files from the source.
  * Random – Randomly select a file from the source folder.
  * None – Use files directly from the source without modification.
* Provides a clean way to manage multiple data folders and item sets
