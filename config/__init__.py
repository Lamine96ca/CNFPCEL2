# Pilote MySQL : mysqlclient s'il est installé (poste de développement),
# sinon PyMySQL (100 % Python, s'installe sans compilation chez o2switch).
try:
    import MySQLdb  # noqa: F401
except ImportError:
    import pymysql
    pymysql.install_as_MySQLdb()
