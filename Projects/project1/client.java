
import javax.net.ssl.*;
import java.io.*;
import java.net.*;
import java.security.*;


public class client
{
	static String host;
	static int defaultPort = 27993;
	static int defaultSSLPort = 27994;
	static String NUID;

	static  String SERVER_PREFIX = "cs5700spring2016";
	public static void main(String argv[]) throws Exception
	{

		boolean portSpecified = false;
		/* Input Validation */
		if(argv.length <2 || argv.length >5)
		{
			System.out.println("Usage: ./client <-p port> <-s> [hostname] [NEU ID]");
		}

		if(argv[0].equals("-p"))
		{
			portSpecified = true;
			try
			{
				defaultPort = Integer.parseInt(argv[1]);
				defaultSSLPort = Integer.parseInt(argv[1]);
			}
			catch(NumberFormatException e)
			{
				System.out.println("Invalid Port number");
				System.exit(0);
			}
		}

		if(portSpecified)
		{
			if(argv[2].equals("-s"))
			{
				host = argv[3];
				NUID = argv[4];
				SSLMode();
			}
			else
			{
				host = argv[2];
				NUID = argv[3];
				NonSSLMode();
			}
		}
		else
		{
			if(argv[0].equals("-s"))
			{
				host = argv[1];
				NUID = argv[2];
				SSLMode();
			}
			else
			{
				host = argv[0];
				NUID = argv[1];
				NonSSLMode();
			}
		}


	}

	public static void NonSSLMode() throws Exception
	{
		String serverResponse = "";

		/* Open a TCP connection with the given host */
		Socket clientSocket = new Socket(host, defaultPort);

		/* Create an outputstream to send messages to the server */
		DataOutputStream outToServer = new DataOutputStream(
				clientSocket.getOutputStream());

		/* Create an inputstream to read messages sent by the server */
		BufferedReader inFromServer = new BufferedReader(new InputStreamReader(
				clientSocket.getInputStream()));

		/* Say hello to the server */

		outToServer.write((SERVER_PREFIX+ " HELLO "+NUID+"\n").getBytes("US-ASCII"));

		/* Read response sent by server  */
		serverResponse = inFromServer.readLine();
		while(!serverResponse.contains("BYE"))
		{

			if(!serverResponse.startsWith(SERVER_PREFIX))
			{
				System.out.println("Corrupt Server Response");
				return;
			}
			if(!( serverResponse.contains("BYE") || serverResponse.contains("STATUS")))
			{
				System.out.println("Corrupt Server Response");
				return;
			}
			String responseTokens[] = serverResponse.split(" ");

			if(responseTokens.length != 5)
			{
				System.out.println("Corrupt Server Response");
				return;
			}

			String code = responseTokens[1];

			int result = 0;
			if(code.equals("STATUS"))
			{


				String operation = responseTokens[3];
				int operand1 = 0,operand2 = 0;

				try
				{
					operand1 = Integer.parseInt(responseTokens[2]);
					operand2 = Integer.parseInt(responseTokens[4]);
				}
				catch(NumberFormatException e)
				{
					System.out.println("Invalid number sent by server");
					return;
				}


				if(operand1 < 1 || operand2 < 1 || operand1 > 1000 || operand2 > 1000)
				{
					System.out.println("CORRUPT RESPONSE");
					return;
				}
				switch (operation) {
				case "+":
					result = operand1 + operand2;
					break;

				case "/":
					result = operand1 / operand2;
					break;

				case "*":
					result = operand1 * operand2;
					break;

				case "-":
					result = operand1 - operand2;
					break;

				default:
					System.out.println("Unknown Mathematical operator. Exiting Program");
					return;
				}


				/* Respond to the server with the result of the arithmetic calculation */
				outToServer.write((SERVER_PREFIX+ " " + result+ "\n").getBytes("US-ASCII"));

				/* Get the next response from the server */
				serverResponse =  inFromServer.readLine();

			}
			else 
			{
				System.out.println("Corrupt Server Response");
				return;
			}

		}


		/* Print the secret flag */
		String splits[] = serverResponse.split(" ");
		if(splits.length == 3 && splits[0].equals(SERVER_PREFIX)&& splits[2].equals("BYE"))
		System.out.println("secret_flag : "+splits[1]);
		else
		{
			System.out.println("Corrupt Server Response");
			return;
		}


		inFromServer.close();
		outToServer.close();
		clientSocket.close();
	}

	public static void SSLMode() throws Exception
	{
		String keystoreloc = "publicKey.store";
		char[] password = "changeit".toCharArray();
		SSLSocketFactory sslSocketFactory = null;

		KeyStore keyStore = KeyStore.
				getInstance(KeyStore.getDefaultType());
		keyStore.load(new FileInputStream(keystoreloc), password);

		TrustManagerFactory trustfactory =
				TrustManagerFactory.getInstance
				(TrustManagerFactory.getDefaultAlgorithm());
		trustfactory.init(keyStore);
		SSLContext context = SSLContext.getInstance("SSL");
		context.init(null, trustfactory.getTrustManagers(), null);
		sslSocketFactory = context.getSocketFactory();

		String serverResponse = "";

		/* Open a TCP connection with the given host */
		SSLSocket clientSocket = (SSLSocket) sslSocketFactory.createSocket(host,defaultSSLPort);

		clientSocket.startHandshake();

		/* Create an outputstream to send messages to the server */
		DataOutputStream outToServer = new DataOutputStream(
				clientSocket.getOutputStream());


		/* Create an inputstream to read messages sent by the server */
		BufferedReader inFromServer = new BufferedReader(new InputStreamReader(
				clientSocket.getInputStream()));

		/* Say hello to the server */
		outToServer.write((SERVER_PREFIX+ " HELLO "+NUID+"\n").getBytes("US-ASCII"));

		/* Read response sent by server  */
		serverResponse = inFromServer.readLine();


		while(!serverResponse.contains("BYE"))
		{
			if(!serverResponse.startsWith(SERVER_PREFIX))
			{
				System.out.println("Corrupt Server Response");
				return;
			}
			if(!( serverResponse.contains("BYE") || serverResponse.contains("STATUS")))
			{
				System.out.println("Corrupt Server Response");
				return;
			}

			String responseTokens[] = serverResponse.split(" ");

			if(responseTokens.length != 5)
			{
				System.out.println("Corrupt Server Response");
				return;
			}

			String code = responseTokens[1];

			int result = 0;
			if(code.equals("STATUS"))
			{
				String operation = responseTokens[3];
				int operand1 = 0,operand2 = 0;

				try
				{
					operand1 = Integer.parseInt(responseTokens[2]);
					operand2 = Integer.parseInt(responseTokens[4]);
				}
				catch(NumberFormatException e)
				{
					System.out.println("Invalid number sent by server");
					return;
				}

				if(operand1 < 1 || operand2 < 1 || operand1 > 1000 || operand2 > 1000)
				{
					System.out.println("CORRUPT RESPONSE");
					return;
				}

				switch (operation) {
				case "+":
					result = operand1 + operand2;
					break;

				case "/":
					result = operand1 / operand2;
					break;

				case "*":
					result = operand1 * operand2;
					break;

				case "-":
					result = operand1 - operand2;
					break;

				default:
					System.out.println("Unknown Mathematical operator. Exiting Program");
					return;
				}


				/* Respond to the server with the result of the arithmetic calculation */
				byte[] res = (SERVER_PREFIX+ " " + result + "\n").getBytes("US-ASCII");
				outToServer.write(res);

				/* Get the next response from the server */
				serverResponse =  inFromServer.readLine();

			}
			else
			{
				System.out.println("CORRUPT RESPONSE");
				return;
			}

		}

		/* Print the secret flag */
		String splits[] = serverResponse.split(" ");
		if(splits.length == 3 && splits[0].equals(SERVER_PREFIX)&& splits[2].equals("BYE"))
		System.out.println("Secret flag: "+splits[1]);
		else
		{
			System.out.println("Corrupt Server Response");
			return;
		}


		inFromServer.close();
		outToServer.close();
		clientSocket.close();

	}
}

