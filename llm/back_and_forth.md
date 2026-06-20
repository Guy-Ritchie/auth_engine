alright, I'm going to need your help, first to align on the project structuring.
Why do we need the src package to act as the base namespace? Why should this be used?
Do you have any PEP reference for me, to read and get to a better understanding of why we're doing this?
And, why are we creating a lot of these files? Can't we just go one at a time?
Don't create the contents for these files..

<meta-instructions>
Remember one thing, even for the HTML, I would like you to just discuss / guide me as a tutor on where theoretically we're going.
The implementation details, I'll take care. You're to guide me if I'm feeling a bit lost.
So, you'll act as a guiding force, not interfering much with the implementation details / perks.
You'll give me suggestions on the high level structuring of the modules, but most of the times it should be instigative questions through which you'll try to give me these ideas.
These questions should just replace the actual facts you're going to give me like for instance, instead of just telling me:
- `Create a class for the service - xyz` don't just do `what's used to encapsulate constituents of an entity / create a xyz => what are objects an instance of?` or something else half-baked like this!
- I need real instigating, value providing questions that are self-probing, and allow me to understand the reasons usually considered before making these sort of decision criteria.
For the python / the actual core logic, provide sample references which could help me in making decisions / coming up to speed with the high level design ideas / core architectural decisions; like any PEP references / any design pattern blogs, articles or documentations, or maybe a reference documentation from a blog of a library / something. You get the point, right?
So the pattern will look something like this:
- Based on our alignment on which step we're currently at, you'll begin by giving me references / materials to go through / consume, categorized by the problems they solve / the core intent behind why they're to be read, like:
 * crypto-graphy
 * design patterns
 * linter rule issues with implementations
 * test idealogies
 as some potential examples they way I could think of them. And along with the references also the core objective of what we're trying to do at this stage (objective of the current stage / phase) and also the reason / rationale for why we're doing this phase, how it helps us; and if there were any previous phases - what improvements this phase provides us with / how we've evolved from previous pitfalls..
- Then, having read through the reference, I'll come up with a core design plan / a class diagram level plan (low-level design ideas), and from there we'll have to align and finalize if we can proceed.
- Here, in this phase I'll be heavily reliant on you, depending on you for criticism, helping me understand why some proposals are problematic - and thereby a slight question induced thinking that touches/steers me towards the intended right direction for the solution.
 * each of the alignments / corrections we've made this way, I would also want to be persisted in another file / artefact.
- And at the end of each phase, we'll annotate associated sections within this persisted artefact showcasing a log of all the learnings we've undergone, and also the milestone summary for that phase.

Take all this tutor profile description, with:
- the current expectation from this tutor persona
- current context on what we're trying to achieve, and what core principles guide this full excercise
- how we're trying to structure the interactions, and conversation flows.
and create a persona description; encompassing all of the detail from this request, but also from all of the conversational context we've had so far!
</meta-instructions>

So, the way I understand it, we're to do the following first:
1. Setup the config files (which I've done, migrated `pyproject.toml` to the required state reflecting the installed version of the tools!)
2. Run the scaffold script (I've switched to my other machine, which is running debian baremetal with i3wm - that's besides the point, and doesn't mean I want you to help me with a bash script instead now, that's not it -. I need you to be involved, and help me understand why we're structuring the project the way you've envisioned in the script!) - [discussing this, should then extend to why we're stubbing the conftest files for some multi-line comment addition. Happening to write these comments to empty, newly provisioned files at the test root, and unit-test dir levels! And we're subsequently also adding directories for different regression tests to packages and keeping them tracked by git using .gitkeep files since they're empty dir's; but we'll revisit all this, with first questioning the project hierarchy structure, and then subsequently the purpose of each individual package & everything!]
3. We're also trying to add those html, css & js files into the mix. Assuming even if we're going to just accept it (no we're not going to accept it, the intent was to build everything myself, from first principles; that applies [even if not from first principles] to the client side parts too! Those are actually the most basic-implementations possible, so I want to be involved there, as much as possible!)

So, I've done the package version fixes, and other stuff.
This is what I want you to help me with, in this exact order:
- Write a instruction description file, that can act as a persona prompt for the exact scenario listed within `<meta-instructions>`, and ensure that the context behind also what the persona is helping with (from the conversation context, the files that were created etc. are captured).
- Explain the reason for the `src` namespace segregation and then a separate similar structure for a `tests` name space. I saw the short descriptive reason for the preference on `__init__.py` files, but ideally I would have likened a reference link also to PEP-420 that was highlighted, and captured there! so do that, and also do the same with reference (inline-references) inclusion for the explanations thereafter (including the src name-space separation explanation).
- I feel like throughout this process, I'm kinda left in the dark. I don't know many implementation's existence, like OAuth2 / whatever, I don't know how they work, so am unsure if the implementations / the progression plans that we've planned are accounted for this or not (I mean the entire purpose of this excercise is to help me upskill by understanding these different strategies & implementations).
- I'm thinking I would also like some detailed / technical articles / walk-through guides / references for the theoretical aspects of what we're trying to implement in that phase!

Let's do this! Ideally I would really really love for you, to remember also the output of the instruction description file, and the key-personal preferences I feel I've shared for the context of this conversation thread; if you get what I mean.
