import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    author: z.string().optional(),
    location: z.string().optional(),
    tags: z.array(z.string()).default([]),
    published: z.boolean().default(true),
    featured: z.boolean().default(false),
    // If you need to redact details, keep the story but remove identifying info.
    redacted: z.boolean().default(false),
  }),
});

export const collections = { posts };
