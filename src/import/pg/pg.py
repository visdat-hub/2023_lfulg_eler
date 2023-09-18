# postgresql connection
from __future__ import unicode_literals
import os, sys
import psycopg2

class db_connector():

    def __init__(self):

        self.db_password = os.environ.get('DB_PASSWORD')
        self.db_user = os.environ.get('DB_USER')
        self.db_port = os.environ.get('DB_PORT')
        self.db_name = os.environ.get('DB_NAME')
        self.db_host = os.environ.get('DB_HOST')
        self.dbConnector = {"error" : None,  "connection" : None,  "query_result" : None}

    def dbConnect(self):

        """db connection string"""
        try:
            connector = psycopg2.connect("dbname='"+self.db_name+"' user='"+self.db_user+"' host='"+self.db_host+"' port='"+self.db_port+"' password='"+self.db_password+"'")
            print('connector',"dbname='"+self.db_name+"' user='"+self.db_user+"' host='"+self.db_host+"' port='"+self.db_port+"' password='"+self.db_password+"'")
            self.dbConnector["connection"] = connector
            print ("OK -> database connection established...")
        except:
            print(sys.exc_info())
            self.dbConnector["error"] = sys.exc_info()
        return self.dbConnector

    def dbClose(self):

        """close connection"""
        try:
            self.dbConnector["connection"].commit()
            self.dbConnector["connection"].close()
            print("OK -> database connection closed...")
        except:
            self.dbConnector["error"] = sys.exc_info()

    def dbCopyFromCsv(self, csv_file, table):

        """copy from csv to db"""
        cur = self.dbConnector["connection"].cursor()
        with open(csv_file, 'r') as f:
            # next(f) Skip the header row.
            try:
                cur.copy_from(f, table, sep=',')
            except:
                self.dbConnector["error"] = sys.exc_info()
                print (sys.exc_info())
        cur.close()
        self.dbConnector["connection"].commit()

    def tblExecute(self, sql):

        """execute sql string"""
        cur = self.dbConnector["connection"].cursor()
        try:
            cur.execute(sql)
        except:
            self.dbConnector["error"] = sys.exc_info()
            print (sys.exc_info())
        cur.close()
        self.dbConnector["connection"].commit()

    def tblInsert(self, table,  columns,  insert_placeholder,  values_json,  return_param):

        """insert values into a table"""
        return_value = None
        if return_param is not None:
            sql = "INSERT INTO " + table + "(" + columns + ") " + \
                "VALUES(" + insert_placeholder + ") RETURNING " + return_param
        else:
            sql = "INSERT INTO " + table + "(" + columns + ") " + \
                "VALUES(" + insert_placeholder + ")"
        print(sql)
        print(values_json)
        cur = self.dbConnector["connection"].cursor()
        try:
            cur.execute(sql,  values_json)
            if return_param is not None:
                return_value = cur.fetchone()[0]

        except:
            self.dbConnector["error"] = sys.exc_info()
            print ("DATABASE ERROR")
            print (sys.exc_info())
            sys.exit()
        cur.close()
        self.dbConnector["connection"].commit()

        return return_value

    def tblDeleteRows(self,  tbl_name, where_condition):

        """delete rows from a table"""
        if where_condition is not None:
            sql = "DELETE FROM " + tbl_name + " WHERE " + where_condition
        else:
            sql =  "DELETE testerror FROM " + tbl_name
        print (sql)
        cur = self.dbConnector["connection"].cursor()
        try:
            cur.execute(sql)
        except:
            self.dbConnector["error"] = sys.exc_info()
            print ("DATABASE ERROR")
            print (sys.exc_info())
        cur.close()
        self.dbConnector["connection"].commit()

    def tblSelect(self, sql):

        """select data from table by using a sql statement"""
        print("--> query data from database... ")
        print (sql)
        query_result = None
        rowcount = 0
        cur = self.dbConnector["connection"].cursor()
        try:
            cur.execute(sql)
            query_result = cur.fetchall()
            rowcount = cur.rowcount
        except:
            self.dbConnector["error"] = sys.exc_info()
            print (sys.exc_info())
        cur.close()
        print("--> row count of query result... " + str(rowcount))
        return query_result,  rowcount