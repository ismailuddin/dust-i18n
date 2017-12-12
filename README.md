# dust-i18n
`dust-i18n` is a Python package for translating `.dust` template files for use with the `makara` internationalisation module in Kraken and Express.JS apps. The package is set up to run inside a Kraken initialised project directory structure, and replace all text strings within the `.dust` template files, with the message tags which point towards the `.properties` files in the `\locales` directory.

`dust-i18n` makes use of the Google Cloud Translation API to automate the translations. Use of this API requires an API key and is not free, although free trials are available.

## Requirements
* Python 3.X
* tqdm (for CLI progress bars)
* google-cloud (Google Cloud Translation API access)

## How it works

The `.dust` file is parsed to extract text strings within html tags, which are replaced using message tags used by `makara` i.e. `{@message type="content" key="UNIQUE_ID"}`.  For each text string, a unique 8 character key is generated comprised of upper-case letters and digits.  A `.properties` file is then generated for the source and destination language, and placed in the appropriate directory of your project.

##### Input dust file

```html
<html>
  <head>
    <title>Page title</title>
  </head>
  <body>
    <div>
      <h1>
        Heading One
      </h1>
      <p>
        Lorem ipsum dolor sit amet
      </p>
    </div>
  </body>
</html>
```

##### Output dust file

```handlebars
{useContent bundle="path/file.properties}
<html>
  <head>
    <title>{@message type="content" key="UVHJ9PLK"}</title>
  </head>
  <body>
    <div>
      <h1>
        {@message type="content" key="DFRTY78K"}
      </h1>
      <p>
        {@message type="content" key="LLJK09YT"}
      </p>
    </div>
  </body>
</html>
{/useContent}
```



## Usage

The simplest way to use this package is using the Kraken project structure.

1. Place the files in the `\dustTranslate` directory into the `\tasks` folder of your Kraken project. 
2. [Acquire](https://cloud.google.com/docs/authentication/getting-started) a JSON private key from the Google Cloud platform to authenticate your access to the API.
3. Set a local system variable for `GOOGLE_APPLICATION_CREDENTIALS` as follows:

```bash
$   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/private_key.json
```

4. Modify the `config.json` file to point to the correct input and output directories for your `.dust` template files. Your input files should be prefixed with `_`, to separate them from your processed output files which are outputted without the underscore.
5. Run the script from the root directory of your project, with the first argument being your destination language.

```bash
$   python tasks/dustTranslate fr
```



## To do / issues

- BeautifulSoup 4 is currently the best solution in Python for parsing HTML files and extracting text, however it does not currently support parsing `.dust` files. Hence, the parser was written from scratch but isn't perfect. Suggestions are welcome.
- Making the package more modular to allow other translation APIs to be used in place of the Google Cloud Translation API
- Unit testing