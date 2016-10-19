import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

// TEAM 4096

public class webcrawler {
	public static String preLoginSessionID = "";
	public static String preLogincsrftoken = "";
	public static String username;
	public static String password;
	public static String targetDomain = "cs5700sp16.ccs.neu.edu";
	public static String sessionID = "";
	public static ArrayList<String> secretFlags = new ArrayList<>();
	
	// Hashset to keep track of visited URLs
	public static HashSet<String> visited = new HashSet<>();
	
	// Queue to hold URLs to be crawled using BFS
	public static LinkedList<String> queue = new LinkedList<>();
	
	
	public static final String secretFlagString = "<h2 class='secret_flag' style=\"color:red\">FLAG: ";
	public static final String hrefRegex = "<a\\s+href\\s*=\\s*(\"[^\"]*\"|[^\\s>]*)\\s*>";

	public static void main(String[] args) {
		//Input Validation
		if (args.length != 2) {
			System.out
					.println("\nInvalid input\nUsage: ./webcrawler <NUID> <PASSWORD>");
		} else {
			username = args[0];
			password = args[1];
			//Begin Crawl
			startStepsToCrawl();
		}
	}
	

	/**
	 * Method that initializes calls to get response from the target domain and calls Login
	 * If login is successful, redirect to Home page and continue crawl.
	 * If login is unsuccessful, report exception
	 */
	public static void startStepsToCrawl() {
		try {
			// Perform Get request on target domain and receive response
			StringBuilder initResponse = doGETInitialResponse();
			String lines[] = initResponse.toString().split("\n");
			//check if status = 200
			if (lines[0].split(" ")[1].equals("200")) {
				//retrieve csrf token and sessionID before login
				for (String line : lines) {
					if (line.startsWith("Set-Cookie: csrftoken=")) {
						preLogincsrftoken = stripID(line);
					}

					if (line.startsWith("Set-Cookie: sessionid=")) {
						preLoginSessionID = stripID(line);
					}
				}
				//Call login after tokens and sessionID is found
				String loginStatus = doLogin();
				
				//if Login is successful, redirect to Home page and crawl
				if (loginStatus.equals("302")) {
					visited.add("/accounts/login/");
					getHomePage();
					crawl();
				} else {
					System.out.println("Login Failed with a status : "
							+ loginStatus);
				}
			}
			//Unable to get csrf tokens and sessionID. Login failed
			else {
				System.out
						.println("Initial GET Request to login page failed : "
								+ lines[0].split(" ")[1]);
			}

		} catch (IOException e) {

			System.out.println("An I/O exception has occured. !! ");
			System.out.println("Here's the stack trace \n");
			System.out.println("-----------------------------------");
			System.out.println(e.getStackTrace());
			System.out.println("----------END OF STACK TRACE ------------");

			e.printStackTrace();
		}
	}

	/**
	 * Method that makes the initial GET request to Fakebook target Domain.
	 * @return response from GET to the target domain
	 */
	public static StringBuilder doGETInitialResponse() {

		Socket clientSocket;
		StringBuilder response = new StringBuilder();
		try {
			clientSocket = new Socket(targetDomain, 80);
			DataOutputStream outToServer = new DataOutputStream(
					clientSocket.getOutputStream());
			BufferedReader inFromServer = new BufferedReader(
					new InputStreamReader(clientSocket.getInputStream()));

			String message = "GET /accounts/login/ HTTP/1.0\n";

			outToServer.write((message + "\n").getBytes("ASCII"));

			String line = "";
			//append each response line to a StringBuilder response
			while ((line = inFromServer.readLine()) != null) {
				response.append(line + "\n");
			}

			clientSocket.close();

		} catch (IOException e) {
			System.out.println("Initial get to target domain failed");
			e.printStackTrace();
		}

		return response;

	}

	/**
	 * Method to make a POST request to login using username, password, sessionID and csrf tokens
	 * @return status for POST request to login
	 */
	public static String doLogin() {

		BufferedReader inFromServer;
		String lines[] = null;
		try {
			Socket clientSocket = new Socket(targetDomain, 80);
			inFromServer = new BufferedReader(new InputStreamReader(
					clientSocket.getInputStream()));
			//POST message to accept username, password, csrf tokens and sessionID received before successful login
			String postMessage = "username=" + username + "&password="
					+ password + "&csrfmiddlewaretoken=" + preLogincsrftoken
					+ "&next=";
			BufferedWriter wr = new BufferedWriter(new OutputStreamWriter(
					clientSocket.getOutputStream()));
			wr.write("POST /accounts/login/ HTTP/1.1\n");
			wr.write("Host: cs5700sp16.ccs.neu.edu\n");
			wr.write("Content-Length:" + postMessage.length() + "\n");
			wr.write("Content-Type: application/x-www-form-urlencoded\n");
			wr.write("Cookie:csrftoken=" + preLogincsrftoken + ";sessionid="
					+ preLoginSessionID + "\n");
			wr.write("\n");
			wr.write(postMessage);
			wr.write("\n");
			wr.flush();
			//Receive response after POST
			StringBuilder response = new StringBuilder();
			String line = "";
			while ((line = inFromServer.readLine()) != null) {
				response.append(line + "\n");
			}

			clientSocket.close();

			lines = response.toString().split("\n");
			//If status after POST is 302 Found, obtain SessionID after login.
			//This sessionID will be used for subsequent GET requests
			if (lines[0].split(" ")[1].equals("302")) {
				for (String s : lines) {
					if (s.startsWith("Set-Cookie: sessionid=")) {
						sessionID = stripID(s);
					}
				}
			}

		} catch (IOException e) {
			System.out.println("Login to fakebook failed");
			e.printStackTrace();
		}

		return lines[0].split(" ")[1];

	}

	/**
	 * Method to make a GET request to the Home page using SessionID after successful login
	 */
	public static void getHomePage() {
		String line = "";
		String status = "";
		boolean success = false;
		StringBuilder response = new StringBuilder();

		try {
			Socket clientSocket = new Socket(targetDomain, 80);
			BufferedWriter outToServer = new BufferedWriter(
					new OutputStreamWriter(clientSocket.getOutputStream()));
			BufferedReader inFromServer;
			inFromServer = new BufferedReader(new InputStreamReader(
					clientSocket.getInputStream()));
			String message = "GET /fakebook/ HTTP/1.0\n";
			outToServer.write(message);
			outToServer.write("Host: cs5700sp16.ccs.neu.edu\n");
			outToServer.write("Connection: close\n");
			outToServer.write("Cookie:csrftoken=" + preLogincsrftoken
					+ ";sessionid=" + sessionID + "\n");
			outToServer.write("\n");
			outToServer.flush();
			//Check if GET request successful
			while ((line = inFromServer.readLine()) != null) {
				if (line.startsWith("HTTP/1.1")) {
					status = line.split(" ")[1];
					if (status.equals("200") || status.equals("302"))
						success = true;
				}
				if (success) {
					response.append(line);
				}

			}
			
			if(success)
			{
				//add Home page to visited
				visited.add("/fakebook/");
				//add links on Home Page to queue
				extractLinkstoQueue(response);
				clientSocket.close();
			}
			else
			{
				clientSocket.close();
				throw new IOException();
			}
			 
		} catch (IOException e) {
			System.out.println("Failed to parse home page");
			e.printStackTrace();
		}

	}
	
	/**
	 * Method that performs the crawl using BFS
	 * @throws IOException
	 */

	public static void crawl() throws IOException {
		while (!queue.isEmpty()) {
			//remove first resource from queue
			String target = queue.removeFirst();
			//Crawl only if target not in visited
			if (!visited.contains(target)) {
				//make a GET request to target
				StringBuilder response = makeGetRequest(target);
				String responselines[] = response.toString().split("\n");

				String statusString = responselines[0];
				int status = Integer.parseInt(statusString.split(" ")[1]);
			
				//If status = 200, check for presence of secret flag and extract links
				if (status == 200) {
					visited.add(target);
					findFlags(response);
					extractLinkstoQueue(response);
				
				} else if (status == 302 || status == 301) {
					//Get redirect URL and add this redirect url to the start of queue
					visited.add(target);
					for (String line : responselines) {
						if (line.startsWith("Location: ")) {
							String loc = line.split("Location: ")[1];
							String redirectLoc = loc
									.split("http://cs5700sp16.ccs.neu.edu")[1];
							if (loc.startsWith("http://cs5700sp16.ccs.neu.edu/")
									&& !visited.contains(redirectLoc)) {
								queue.addFirst(redirectLoc);
							}
						}
					}
				} else if (status == 500) {
					//retry GET by adding this target to start of queue
					queue.addFirst(target);
				} else {
					//if 404 or 401 or any other status, ignore
					visited.add(target);
					// do nothing
				}

			}
		}
	}

	/**
	 * Method to extract <a href ...> links from the response
	 * @param response is the response received after making a GET request to a resource
	 */
	public static void extractLinkstoQueue(StringBuilder response) {

		Pattern pat = Pattern.compile(hrefRegex, Pattern.CASE_INSENSITIVE);
		Matcher urlMatcher = pat.matcher(response);

		while (urlMatcher.find()) {
			int begin = urlMatcher.start();
			int end = urlMatcher.end();
			//strip "<a href" tag to obtain resource url
			String foundURL = response.substring(begin + 9, end - 2);
			if (isValid(foundURL)) {
				queue.add(foundURL);
			}
		}
	}
	
	

	/**
	 *  This is custom GET method for each resource that the crawler crawls. 
	 * @param target is the target resource
	 * @return a StringBuilder response for the GET request
	 * @throws IOException
	 */
	public static StringBuilder makeGetRequest(String target)
			throws IOException {
		Socket clientSocket = new Socket(targetDomain, 80);
		
		PrintWriter outToServer = new PrintWriter(new OutputStreamWriter(
				clientSocket.getOutputStream()));
		BufferedReader inFromServer = new BufferedReader(new InputStreamReader(
				clientSocket.getInputStream()));

		String message = "GET " + target + " HTTP/1.0\n";
		outToServer.print(message);
		outToServer.print("Host: cs5700sp16.ccs.neu.edu\n");
		outToServer.print("Connection: close\n");
		outToServer.print("Cookie:csrftoken=" + preLogincsrftoken
				+ ";sessionid=" + sessionID + "\n");
		outToServer.print("\n");
		outToServer.flush();

		StringBuilder response = new StringBuilder();
		String line = "";
		while ((line = inFromServer.readLine()) != null) {
			response.append(line + "\n");
		}

		outToServer.close();
		inFromServer.close();
		clientSocket.close();

		return response;

	}

	/**
	 * Method that looks through response to check for hidden flags
	 * @param response is the response for the link that is crawled by the crawler
	 */
	public static void findFlags(StringBuilder response) {
		String body = response.toString();
		//search for secret flag string
		if (body.contains("class='secret_flag'")) {
			//find start index of string
			int startIndex = response.indexOf(secretFlagString);
			//strip 64 bit alphanumeric flag
			String flag = response.substring(
					startIndex + secretFlagString.length(), startIndex
							+ secretFlagString.length() + 64);
			System.out.println(flag);
			secretFlags.add(flag);
			if (secretFlags.size() == 5) {
				//quit when all 5 flags are found
				System.exit(0);
			}
		}
	}

	/**
	 * Method to check if the url is valid (belongs to target domain and not in visited) before adding to the Queue
	 * @param url is the url that needs to be validated
	 * @return true if the url should be added to the queue, false otherwise
	 */
	public static boolean isValid(String url) {
		return (url.startsWith("/") && !visited.contains(url));
	}

	/**
	 * Method to strip the sessionID or the csrf token from response line
	 * @param line is the response line that contains the token or sessionID
	 * @return the stripped string that holds the csrf token or sessionID
	 */
	public static String stripID(String line) {
		{
			String keyValue = line.split(" ")[1].split("=")[1];
			return keyValue.substring(0, keyValue.length() - 1);
		}
	}

}
