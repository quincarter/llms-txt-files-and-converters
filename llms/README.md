## LLMs

These LLMs txt files are ingestible raw text files generated from site-specific documentation that LLMs can read to gain a better understanding of a particular technology or library. 

### Considerations

Each of these files is gigantic and will consume literally all of your context. The best way to handle these would be to create a custom MCP to search docs for a specific technology so that it can hone in and focus the docs appropriately. 

Adding just one of these files to your copilot or gemini context will cause a summarization or compact task to occur nearly immediately, or the request will fail for being too large. Which is the opposite of what is intended by providing these files. 

One way to use this would also be to add one of these to your repo, and have the agent reference these docs or search the docs for the approrpirate information. 