import { motion } from "framer-motion";
import { Navbar } from "@/components/layout/navbar";
import { LandingFooter } from "@/components/landing/landing-footer";
import { Calendar, User, ArrowRight } from "lucide-react";

export default function BlogPage() {
  const blogPosts = [
    {
      id: 1,
      title: "10 Tips for Choosing the Perfect Salon",
      excerpt: "Learn how to find a salon that matches your style and needs.",
      author: "Sarah Johnson",
      date: "January 15, 2024",
      category: "Tips",
    },
    {
      id: 2,
      title: "Hair Care Tips for Healthy Hair",
      excerpt:
        "Discover professional tips to maintain healthy and beautiful hair.",
      author: "Michael Chen",
      date: "January 10, 2024",
      category: "Hair Care",
    },
    {
      id: 3,
      title: "Latest Hair Trends for 2024",
      excerpt: "Stay updated with the hottest hair trends this year.",
      author: "Emma Davis",
      date: "January 5, 2024",
      category: "Trends",
    },
    {
      id: 4,
      title: "How to Prepare for Your First Salon Visit",
      excerpt: "Everything you need to know before your first appointment.",
      author: "James Wilson",
      date: "December 28, 2023",
      category: "Guide",
    },
    {
      id: 5,
      title: "Salon Etiquette 101",
      excerpt: "Learn the dos and don'ts of salon etiquette.",
      author: "Lisa Anderson",
      date: "December 20, 2023",
      category: "Etiquette",
    },
    {
      id: 6,
      title: "Budget-Friendly Hair Care Solutions",
      excerpt: "Get salon-quality results without breaking the bank.",
      author: "David Martinez",
      date: "December 15, 2023",
      category: "Budget",
    },
  ];

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <motion.div
            className="max-w-5xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl font-bold mb-4">Kenikool Blog</h1>
            <p className="text-xl text-muted-foreground mb-12">
              Tips, trends, and insights for salon owners and beauty enthusiasts
            </p>

            {/* Blog Posts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {blogPosts.map((post, idx) => (
                <motion.div
                  key={post.id}
                  className="bg-card border border-border rounded-lg overflow-hidden hover:border-primary transition-colors cursor-pointer group"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: idx * 0.1 }}
                >
                  <div className="bg-linear-to-br from-primary/20 to-secondary/20 h-48 flex items-center justify-center">
                    <div className="text-6xl opacity-20">📝</div>
                  </div>
                  <div className="p-6">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-xs font-semibold text-primary bg-primary/10 px-3 py-1 rounded-full">
                        {post.category}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold mb-3 group-hover:text-primary transition-colors">
                      {post.title}
                    </h3>
                    <p className="text-muted-foreground mb-4">{post.excerpt}</p>
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1">
                          <User size={14} />
                          {post.author}
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar size={14} />
                          {post.date}
                        </div>
                      </div>
                      <ArrowRight
                        size={18}
                        className="group-hover:translate-x-1 transition-transform"
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </main>
      <LandingFooter />
    </div>
  );
}
