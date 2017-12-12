# dust-i18n
`dust-i18n` is a Python package for translating `.dust` template files for use with the `makara` internationalisation module in Kraken and Express.JS apps. The package is set up to run inside a Kraken initialised project directory structure, and replace all text strings within the `.dust` template files, with the message tags which point towards the `.properties` files in the `\locales` directory.

`dust-i18n` makes use of the Google Cloud Translation API to automate the translations. Use of this API requires an API key and is not free, although free trials are available.

## Requirements
* Python 3.X
* tqdm (for CLI progress bars)
* google-cloud (Google Cloud Translation API access)

## Usage
The simplest way to use this package is using the Kraken project structure.
1. Place the files in the `\dustTranslate` directory into the `\tasks` folder of your Kraken project. 

2. [Acquire](https://cloud.google.com/storage/docs/authentication) a JSON private key from the Google Cloud platform to authenticate your access to the API.

3. Modify the `config.json` file to point to the correct input and output directories for your `.dust` template files. I recommend prefixing your files with `_`, to separate them from your processed output files.

4. Run the script from the root directory of your project, with the first argument being your destination language.
```bash
$   python tasks/dustTranslate fr
```