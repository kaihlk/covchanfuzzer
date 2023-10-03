pylint --module-rgx='[a-zA-Z_]\w*' --include-naming-hint=y -f mpy > classes.dot
dot -Tpng classes.dot -o classes.png