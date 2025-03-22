// Read in debug.properties file and output the Java interpretation.
//
// This file is intended for debugging purposes.  Make your changes to a file
// called debug.properties and observe the Java interpretation.
//
// To compile:
//    javac properties.java
//
// To run:
//    java properties

import java.util.*;
import java.io.*;

class properties{
	public static void main(String args[]) {

		Properties properties = new Properties();
		try {
		    properties.load(new FileInputStream("debug.properties"));
		    PrintWriter outwriter = new PrintWriter(System.out);
		    properties.list(System.out);
		    System.out.println(properties);
		    outwriter.flush();
		} catch (IOException e) {
			System.out.println("Some error occured");
		}
	}
}

