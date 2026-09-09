export type ContentType = "Report" | "Publication" | "Dataset" | "Photo" | "Video" | "News" | "Learning";

export type RepositoryItem = {
  id: string;
  type: ContentType;
  title: string;
  summary: string;
  year: number;
  region: "Antarctica" | "Arctic" | "Southern Ocean";
  topics: string[];
  meta: string;
  accent: string;
  icon: string;
};

export const heroImage = "/manus-storage/polaris-hero_efcb01ef.png";

export const navItems = [
  { href: "/explorer", label: "Explorer" },
  { href: "/repository", label: "Repository" },
  { href: "/learn", label: "Learn" },
  { href: "/assistant", label: "Assistant" },
  { href: "/media", label: "Media" },
];

export const stats = [
  { value: "124", label: "Expedition records" },
  { value: "68", label: "Publications" },
  { value: "2.4k", label: "Media assets" },
  { value: "18", label: "Learning paths" },
];

export const repositoryItems: RepositoryItem[] = [
  { id: "exp-43", type: "Report", title: "43rd Indian Antarctic Expedition", summary: "A field report on atmospheric observations, glaciology and biological sampling conducted across the Maitri region.", year: 2023, region: "Antarctica", topics: ["Expedition", "Climate change", "Glaciology"], meta: "PDF · 86 pages", accent: "from-cyan-300/30 via-sky-500/10 to-transparent", icon: "▱" },
  { id: "ocean-24", type: "Dataset", title: "Southern Ocean Carbon Flux Observations", summary: "Curated measurements from transects around the Indian Ocean sector of Antarctica.", year: 2024, region: "Southern Ocean", topics: ["Oceanography", "Climate change"], meta: "CSV · 14.2 MB", accent: "from-emerald-300/25 via-teal-500/10 to-transparent", icon: "⌁" },
  { id: "maitri-paper", type: "Publication", title: "Snow accumulation dynamics near Maitri Station", summary: "Peer-reviewed analysis of seasonal snow accumulation and its relationship to surface energy balance.", year: 2022, region: "Antarctica", topics: ["Glaciology", "Maitri"], meta: "Journal article · 12 min read", accent: "from-indigo-300/30 via-violet-500/10 to-transparent", icon: "✦" },
  { id: "bharati-video", type: "Video", title: "Inside Bharati: India’s polar laboratory", summary: "A short visual field note from the newest of India’s Antarctic research stations.", year: 2024, region: "Antarctica", topics: ["Stations", "Education"], meta: "Video · 04:18", accent: "from-orange-300/25 via-amber-500/10 to-transparent", icon: "▶" },
  { id: "arctic-brief", type: "News", title: "New observations strengthen Arctic–monsoon links", summary: "Researchers share early insights from India’s Arctic research programme and its climate connections.", year: 2024, region: "Arctic", topics: ["Climate change", "Arctic"], meta: "News · 5 min read", accent: "from-pink-300/25 via-fuchsia-500/10 to-transparent", icon: "↗" },
  { id: "polar-101", type: "Learning", title: "Polar Science 101", summary: "A beginner-friendly introduction to ice, oceans, climate systems and the scientists who study them.", year: 2024, region: "Antarctica", topics: ["Education", "Basics"], meta: "Lesson · 8 min", accent: "from-yellow-200/30 via-cyan-500/10 to-transparent", icon: "◎" },
  { id: "photo-ice", type: "Photo", title: "Field notes: blue ice and long shadows", summary: "A photo essay from the summer traverse documenting wind-carved ice formations.", year: 2021, region: "Antarctica", topics: ["Photography", "Fieldwork"], meta: "Gallery · 18 images", accent: "from-sky-300/30 via-blue-600/10 to-transparent", icon: "▧" },
  { id: "tech-station", type: "Publication", title: "Designing for the cold: polar technology", summary: "How instruments, shelters and field protocols are adapted for reliable work in extreme environments.", year: 2020, region: "Antarctica", topics: ["Technology", "Stations"], meta: "Explainer · 10 min read", accent: "from-teal-300/25 via-slate-500/10 to-transparent", icon: "⌘" },
];

export const stations = [
  { id: "maitri", name: "Maitri", region: "Schirmacher Oasis, Antarctica", established: "1989", number: "01", description: "India’s second permanent Antarctic station, supporting atmospheric, glaciological, geological and biological research.", facts: ["71°45′S · 11°44′E", "Summer + winter operations", "Polar earth sciences"], color: "cyan" },
  { id: "bharati", name: "Bharati", region: "Larsemann Hills, Antarctica", established: "2012", number: "02", description: "A modern coastal station enabling research across ocean, climate, life and earth science disciplines.", facts: ["69°24′S · 76°11′E", "Coastal research base", "Ocean & climate"], color: "amber" },
  { id: "himadri", name: "Himadri", region: "Ny-Ålesund, Svalbard", established: "2008", number: "03", description: "India’s Arctic research station, opening a window into sea ice, glaciers and high-latitude climate processes.", facts: ["79°N · 11°E", "Arctic summer research", "Cryosphere studies"], color: "violet" },
];

export const stationCoordinates: Record<string, { left: string; top: string }> = { maitri: { left: "43%", top: "58%" }, bharati: { left: "67%", top: "42%" }, himadri: { left: "78%", top: "17%" } };

export const learningTopics = [
  { id: "polar-101", title: "Polar Science 101", tag: "Start here", description: "The essentials of ice, oceans, climate and polar fieldwork.", progress: 62, color: "cyan" },
  { id: "antarctica-arctic", title: "Antarctica vs Arctic", tag: "Compare", description: "Two poles, two systems, one connected planet.", progress: 18, color: "indigo" },
  { id: "climate", title: "Climate change", tag: "Explore", description: "Read the signals recorded in ice, air and ocean.", progress: 0, color: "emerald" },
  { id: "glaciology", title: "Glaciology", tag: "Deep dive", description: "How glaciers move, melt and remember climate.", progress: 0, color: "sky" },
  { id: "oceans", title: "Polar oceans", tag: "Explore", description: "Currents, carbon and the ocean around the ice.", progress: 0, color: "teal" },
  { id: "stations", title: "India’s stations", tag: "Field notes", description: "Meet Maitri, Bharati and Himadri.", progress: 0, color: "amber" },
];

export const quizQuestions = [
  { question: "Which Indian station is located in the Arctic?", options: ["Maitri", "Bharati", "Himadri", "Dakshin Gangotri"], answer: 2 },
  { question: "What does glaciology study?", options: ["Clouds", "Ice and glaciers", "Deep ocean fish", "Auroras"], answer: 1 },
  { question: "Why are polar regions important to climate science?", options: ["They have no weather", "They store signals of Earth’s climate", "They are closest to the Sun", "They never change"], answer: 1 },
];

export const assistantAnswer = {
  full: "India’s 43rd Antarctic Expedition brought together atmospheric, glaciological, biological and earth-science programmes around Maitri and the wider Schirmacher Oasis. The expedition’s work helped teams observe seasonal changes in snow and ice, measure atmospheric conditions, and collect field samples for longer-term climate and ecosystem studies.",
  simple: "India’s 43rd Antarctic Expedition was a science trip to study ice, weather, rocks and living things near the Maitri station. Scientists collected observations that help us understand how Antarctica is changing and how those changes can affect the rest of the planet.",
  sources: ["43rd Indian Antarctic Expedition · Expedition report · 2023", "Snow accumulation dynamics near Maitri Station · Publication · 2022"],
};

export const mediaStories = [
  { id: "m1", type: "Field note", eyebrow: "Antarctica · 08 min", title: "A day in the field at Maitri", summary: "From first light to the evening weather log, follow a day shaped by wind, ice and teamwork.", gradient: "from-cyan-950 via-sky-900 to-slate-800" },
  { id: "m2", type: "Video", eyebrow: "Bharati · 04:18", title: "Inside India’s coastal polar laboratory", summary: "A visual introduction to the systems and people that keep Bharati moving.", gradient: "from-amber-950 via-orange-900 to-slate-800" },
  { id: "m3", type: "Photo essay", eyebrow: "Fieldwork · 18 images", title: "Blue ice, long shadows", summary: "A quiet collection of textures, horizons and patterns from a summer traverse.", gradient: "from-indigo-950 via-blue-900 to-slate-800" },
  { id: "m4", type: "News", eyebrow: "Arctic · 05 min", title: "What the Arctic is teaching us about monsoons", summary: "New observations prompt a closer look at the links between high latitudes and India’s weather.", gradient: "from-violet-950 via-fuchsia-900 to-slate-800" },
];

export const outreachChannels = [
  { id: "web", label: "Website article", icon: "◒", content: "India’s 43rd Antarctic Expedition brought together scientists studying ice, atmosphere, ocean and life around Maitri Station. Their field observations help build a clearer picture of Antarctica’s changing environment — and the connections that reach far beyond the continent." },
  { id: "linkedin", label: "LinkedIn", icon: "in", content: "From snow accumulation to atmospheric observations, India’s 43rd Antarctic Expedition is advancing the evidence base for polar and climate science. Explore the field report and the teams behind the data." },
  { id: "instagram", label: "Instagram", icon: "◎", content: "What does a polar expedition actually study? Ice. Air. Ocean. Life. And the connections between them. Follow the field notes from India’s 43rd Antarctic Expedition." },
  { id: "x", label: "X post", icon: "𝕏", content: "India’s 43rd Antarctic Expedition turns field observations into climate knowledge — from snow and ice to atmosphere and life around Maitri Station." },
  { id: "education", label: "Educational post", icon: "✦", content: "Did you know? Snow can store clues about Antarctica’s climate. During India’s 43rd Antarctic Expedition, researchers observed the ice, air and landscape to understand how polar systems are changing." },
  { id: "newsletter", label: "Newsletter", icon: "✉", content: "This month from the poles: field observations from Maitri, a new look at Southern Ocean carbon flux, and a beginner’s guide to the science of ice. Read, learn and explore with Polar Connect." },
];

export const promptChips = ["Indian Antarctic expeditions 2018–2024", "What happens at Maitri?", "Explain polar science for Class 10"];
export const allTopics = Array.from(new Set(repositoryItems.flatMap((item) => item.topics))).sort();
export const years = [2024, 2023, 2022, 2021, 2020];
export const contentTypes = ["All types", "Report", "Publication", "Dataset", "Photo", "Video", "News", "Learning"] as const;
export const allRegions = ["All regions", "Antarctica", "Arctic", "Southern Ocean"] as const;
export const topicColorMap: Record<string, string> = { cyan: "from-cyan-400/30 to-sky-500/10", indigo: "from-indigo-400/30 to-violet-500/10", emerald: "from-emerald-400/30 to-teal-500/10", sky: "from-sky-400/30 to-blue-500/10", teal: "from-teal-400/30 to-cyan-500/10", amber: "from-amber-400/30 to-orange-500/10", violet: "from-violet-400/30 to-fuchsia-500/10" };
export const routeLabels: Record<string, string> = { "/": "Overview", "/repository": "Repository", "/assistant": "Assistant", "/learn": "Learning", "/explorer": "Explorer", "/media": "Media", "/studio": "Outreach Studio", "/about": "About" };
export const institution = { department: "National Centre for Polar and Ocean Research", ministry: "Ministry of Earth Sciences · Government of India", short: "NCPOR" };
export const footerLinks = [{ label: "About NCPOR", href: "/about" }, { label: "Content provenance", href: "/about#provenance" }, { label: "Accessibility", href: "/about#accessibility" }, { label: "Contact", href: "/about#contact" }];
export const getItem = (id: string) => repositoryItems.find((item) => item.id === id);
export const getTopic = (id: string) => learningTopics.find((topic) => topic.id === id) ?? learningTopics[0];
export const getStation = (id: string) => stations.find((station) => station.id === id) ?? stations[0];
export const getMedia = (id: string) => mediaStories.find((story) => story.id === id) ?? mediaStories[0];
export const iconForType: Record<ContentType, string> = { Report: "▱", Publication: "✦", Dataset: "⌁", Photo: "▧", Video: "▶", News: "↗", Learning: "◎" };
export const colorForType: Record<ContentType, string> = { Report: "bg-cyan-100 text-cyan-800", Publication: "bg-violet-100 text-violet-800", Dataset: "bg-emerald-100 text-emerald-800", Photo: "bg-sky-100 text-sky-800", Video: "bg-amber-100 text-amber-800", News: "bg-pink-100 text-pink-800", Learning: "bg-indigo-100 text-indigo-800" };
export const studioSteps = ["Uploaded", "Analysed", "Drafted", "Review", "Approved"] as const;
export const statusCopy: Record<(typeof studioSteps)[number], string> = { Uploaded: "Source record received", Analysed: "Metadata extracted", Drafted: "Channels generated", Review: "Awaiting human review", Approved: "Ready for publishing" };
export const homeTitle = "The poles are telling a story. Start listening.";
export const homeDescription = "Polar Connect brings expeditions, evidence, field notes and learning into one intelligent public space — built for researchers, students and everyone curious about our changing planet.";
export const assistantDescription = "Ask a question in plain language. Polar Connect retrieves from the repository, explains the answer, and shows you the source.";
export const repositoryDescription = "Browse the growing public record of India’s polar research — from expedition reports to classroom-ready explainers.";
export const learnDescription = "Turn complex polar science into clear lessons, visual explainers and small wins you can remember.";
export const explorerDescription = "Follow India’s stations and expedition routes across the high latitudes.";
export const mediaDescription = "Field notes, stories and visual dispatches from the people and places behind the research.";
export const studioDescription = "Turn one trusted source into clear, review-ready content for every channel.";
export const aboutDescription = "A public knowledge and outreach layer for India’s polar science ecosystem.";
export const appDescription = "An AI-powered polar science knowledge and outreach platform for NCPOR.";
export const copyright = "© 2026 Polar Connect · NCPOR / Ministry of Earth Sciences";
export const demoNotice = "Demo records mapped to NCPOR themes · Connect institutional APIs for live records";
export const shadowCard = "shadow-[0_16px_48px_rgba(8,28,45,0.08)]";
export const sectionTitleClass = "font-display text-3xl font-semibold tracking-[-0.04em] text-[#102333] md:text-5xl";
export const eyebrowClass = "text-[11px] font-bold uppercase tracking-[0.22em] text-cyan-700";
export const bodyCopyClass = "text-[15px] leading-7 text-[#5e7180]";
export const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(" ");
export const featuredExpedition = repositoryItems[0];
export const latestItems = [repositoryItems[4], repositoryItems[3], repositoryItems[6]];
export const recommendedLearning = learningTopics.slice(0, 3);
export type Station = (typeof stations)[number];
export type Topic = (typeof learningTopics)[number];
export type MediaStory = (typeof mediaStories)[number];
export type OutreachChannel = (typeof outreachChannels)[number];
export type QuizQuestion = (typeof quizQuestions)[number];
export type StudioStep = (typeof studioSteps)[number];
