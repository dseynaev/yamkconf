# yamkconf

yamkconf is an utility to convert YAML-documents embedded in a Makefile into variable declarations. This repository hosts a proof-of-concept implementation in python.

The source file is a 'Makefile.yamk' file which contains make directives and YAML-documents separated with the usual `---` and `...` stream-based syntax. The content of the YAML documents can be accessed in the makefile by descending the hierarchy using `.`

The result is a plain Makefile.
As such, the build process consists of:

```
./yamkconf.py
make <target>
```

## remote references

The parser extends the default YAML syntax with an `%INCLUDE` directive. By using this directive, the content of YAML documents can be included in-line into an embedded document. This allows referencing to anchors defined in the included documents.

## example

see /example
