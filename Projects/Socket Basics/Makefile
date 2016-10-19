JFLAGS = -g
JC = javac
JVM= java 
.SUFFIXES: .java .class
.java.class:
	$(JC) $(JFLAGS) $*.java

CLASSES = client.java \
     
default: classes

classes: $(CLASSES:.java=.class)


MAIN = client
run: $(MAIN).class
	$(JVM) $(MAIN)

clean:
	$(RM) *.class
